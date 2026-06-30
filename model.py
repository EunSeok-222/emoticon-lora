import os
import torch
import numpy as np
import streamlit as st
from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    StableDiffusionPipeline,
    UniPCMultistepScheduler,
)
from peft import PeftModel
from PIL import Image

DEVICE = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
MODEL_ID = "runwayml/stable-diffusion-v1-5"
LORA_PATH = os.path.join(os.path.dirname(__file__), "lora_animal", "epoch_7")
CONTROLNET_ID = "lllyasviel/sd-controlnet-scribble"


@st.cache_resource(show_spinner=False)
def load_pipeline():
    token = st.secrets.get("HF_TOKEN", None)

    pipe_base = StableDiffusionPipeline.from_pretrained(
        MODEL_ID, torch_dtype=torch.float32, token=token
    )
    pipe_base.unet = PeftModel.from_pretrained(pipe_base.unet, LORA_PATH)

    controlnet = ControlNetModel.from_pretrained(
        CONTROLNET_ID, torch_dtype=torch.float32, token=token
    )

    pipe = StableDiffusionControlNetPipeline(
        vae=pipe_base.vae,
        text_encoder=pipe_base.text_encoder,
        tokenizer=pipe_base.tokenizer,
        unet=pipe_base.unet,
        controlnet=controlnet,
        scheduler=UniPCMultistepScheduler.from_config(pipe_base.scheduler.config),
        safety_checker=None,
        feature_extractor=None,
        requires_safety_checker=False,
    )
    pipe = pipe.to(DEVICE)
    pipe.enable_attention_slicing(1)
    pipe.enable_vae_slicing()
    return pipe


def _pad_to_square(img: Image.Image) -> Image.Image:
    """종횡비를 유지하며 흰 배경으로 정방형 패딩 (찌그러짐 방지)"""
    w, h = img.size
    size = max(w, h)
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    canvas.paste(img, ((size - w) // 2, (size - h) // 2))
    return canvas


def _binarize(img: Image.Image) -> Image.Image:
    """회색/유색 배경 → 흰색, 선 → 검정으로 이진화 (ControlNet scribble 최적 입력)"""
    arr = np.array(img.convert("L"))
    binary = np.where(arr < 128, 0, 255).astype(np.uint8)
    return Image.fromarray(binary).convert("RGB")


def convert_sketch(
    pipe,
    sketch_img: Image.Image,
    steps: int = 30,
    guidance: float = 7.5,
    cn_scale: float = 0.8,
) -> Image.Image:
    # 전처리: 정방형 패딩 → 이진화 → 512 리사이즈
    control_img = _binarize(_pad_to_square(sketch_img)).resize(
        (512, 512), Image.LANCZOS
    )
    prompt = (
        "twemoji style, cute animal face emoticon, "
        "flat color, white background, simple illustration, single character"
    )
    negative = (
        "realistic, photo, blurry, dark, ugly, text, watermark, "
        "multiple animals, full body, pattern, collage, many faces, busy background"
    )
    with torch.no_grad():
        result = pipe(
            prompt=prompt,
            negative_prompt=negative,
            image=control_img,
            num_inference_steps=steps,
            guidance_scale=guidance,
            controlnet_conditioning_scale=cn_scale,
        ).images[0]
    return result
