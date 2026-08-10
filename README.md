<div align="center">

# 🎨 손그림 → 이모티콘

**스케치북에 대충 그린 낙서를 AI가 twemoji 스타일 동물 이모티콘으로 바꿔줍니다.**

Stable Diffusion v1.5에 **동물 이모티콘 스타일 LoRA**를 파인튜닝하고,
**ControlNet(scribble)** 으로 손그림의 구도를 그대로 살려 변환하는 개인 딥러닝 포트폴리오 프로젝트입니다.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)]()
[![Stable Diffusion](https://img.shields.io/badge/Stable_Diffusion-v1.5%20%2B%20LoRA-8A2BE2)]()
[![ControlNet](https://img.shields.io/badge/ControlNet-scribble-1C3C3C)]()
[![PEFT](https://img.shields.io/badge/PEFT-LoRA-FFB000)]()

🚀 **[앱 데모(HF Spaces)](https://huggingface.co/spaces/eunseok22/emoticon-lora)** · 🎬 **[발표 슬라이드](https://eunseok-222.github.io/emoticon-lora/presentation/)**

</div>

---

## 📌 프로젝트 정보

|  |  |
|---|---|
| **프로젝트명** | 손그림 → 이모티콘 (emoticon-lora) |
| **개발 기간** | ~2026.07 (개인 프로젝트) |
| **개발 인원** | 1인 — 데이터 수집·정제부터 LoRA 학습, 파이프라인 구성, Streamlit 앱까지 전 과정 단독 개발 |
| **핵심 개념** | 손그림 스케치 업로드 → 이진화·정방형 전처리 → ControlNet으로 구도 고정 → LoRA 파인튜닝된 SD1.5로 twemoji 스타일 생성 |
| **배포** | Hugging Face Spaces — [huggingface.co/spaces/eunseok22/emoticon-lora](https://huggingface.co/spaces/eunseok22/emoticon-lora) |

> 이전에 별도 리포(`emoticon-presentation`)로 분리돼 있던 발표 슬라이드를 이 저장소의 [`docs/presentation/`](docs/presentation)로 통합했습니다.

---

## ✨ 핵심 기능

| 기능 | 설명 |
|------|------|
| ✏️ **손그림 → 이모티콘 변환** | 업로드한 스케치를 정방형 패딩 + 이진화(흑백)로 전처리 후 ControlNet(scribble)에 입력해 원본 구도를 유지하며 생성 |
| 🎨 **LoRA 파인튜닝** | `runwayml/stable-diffusion-v1-5` UNet에 diffusers/PEFT 네이티브 LoRA를 적용, twemoji 스타일 동물 이모티콘 데이터로 파인튜닝(최종 채택: epoch 7) |
| 📊 **학습 리포트 (앱 내장)** | Streamlit 멀티페이지로 학습 곡선, EDA/데이터 분석, LoRA 가중치 분석, epoch별 생성 품질 비교를 인터랙티브하게 제공 |
| 🎬 **발표 슬라이드** | 프로젝트 개요부터 데이터 수집·학습·트러블슈팅·최종 결과까지 정리한 16:9 웹 슬라이드 덱 (`docs/presentation/`) |

---

## 📖 발표 슬라이드 목차

1. 프로젝트 개요
2. 사용 기술 & 선정 이유
3. 시스템 아키텍처 / 파이프라인
4. 데이터셋 수집 · 정제 · 증강
5. 학습 설정 (하이퍼파라미터)
6. 학습 진행 — Epoch별 생성 샘플
7. 학습 곡선 분석
8. 문제 발견 & 개선
9. 최종 결과
10. 분석 — 생성 품질 · 가중치 · 데이터
11. 배포 & 데모
12. 결론 & 느낀 점

---

## 🗂 아키텍처

```
손그림 스케치 업로드
   │
   ▼
전처리 (정방형 패딩 → 이진화 → 512×512 리사이즈)
   │
   ▼
ControlNet(scribble) — 원본 구도 고정
   │
   ▼
Stable Diffusion v1.5 UNet + LoRA(twemoji 스타일, epoch 7) — DPM-Solver++ 스케줄러
   │
   ▼
twemoji 스타일 동물 이모티콘 생성
```

- LoRA는 PEFT 네이티브 포맷(`adapter_config.json` + `adapter_model.safetensors`)으로 `lora_animal/epoch_7/`에 저장
- `torch.backends.mps` 자동 감지로 Apple Silicon(M1) 환경도 지원, `PYTORCH_ENABLE_MPS_FALLBACK=1` 기본 적용

---

## 🛠 기술 스택

| 영역 | 사용 기술 |
|------|----------|
| **생성 모델** | Stable Diffusion v1.5(`runwayml/stable-diffusion-v1-5`) · ControlNet(`lllyasviel/sd-controlnet-scribble`) |
| **파인튜닝** | diffusers + PEFT 네이티브 LoRA |
| **프레임워크** | PyTorch · torchvision · accelerate · safetensors |
| **앱** | Streamlit (멀티페이지: 학습 리포트 · 그래프 · EDA · 가중치 분석 · 생성 품질) |
| **시각화** | matplotlib, numpy |
| **배포** | Hugging Face Spaces |

---

## 🗃 저장소 구성

| 경로 | 설명 |
|---|---|
| `app.py` | 메인 Streamlit 앱 — 스케치 업로드 → 변환 결과 표시 |
| `model.py` | 파이프라인 로딩(SD1.5 + LoRA + ControlNet) 및 스케치 전처리·생성 로직 |
| `pages/` | 학습 리포트 · 성능 그래프 · EDA 데이터 분석 · 가중치 분석 · 생성 품질 비교 (Streamlit 멀티페이지) |
| `lora_animal/epoch_7/` | 최종 채택된 LoRA 가중치(PEFT 포맷) |
| `animal_samples/` | 예시 스케치·생성 결과, epoch별 생성 샘플 이미지 |
| `emoticon.ipynb` | 데이터 전처리·LoRA 학습 노트북 |
| `docs/presentation/` | 발표 슬라이드(`index.html`) + 발표용 이미지 자산(`emoticon_deck_assets/`) — [GitHub Pages로 배포](https://eunseok-222.github.io/emoticon-lora/presentation/) |

---

## ⚡ 시작하기

```bash
git clone https://github.com/EunSeok-222/emoticon-lora.git
cd emoticon-lora
pip install -r requirements.txt

streamlit run app.py
```

- Hugging Face 비공개 모델 접근이 필요하면 `.streamlit/secrets.toml`에 `HF_TOKEN`을 등록합니다.
- Apple Silicon(M1/M2)에서는 `device="mps"`가 자동 선택됩니다. CUDA GPU가 있으면 자동으로 `cuda`를 사용합니다.

## 🎬 발표 슬라이드 로컬에서 보기

```bash
open docs/presentation/index.html
```
