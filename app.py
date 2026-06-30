import os
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import io, base64, hashlib
import streamlit as st
from PIL import Image
from model import load_pipeline, convert_sketch

st.set_page_config(page_title="손그림 → 이모티콘", page_icon="✏️", layout="centered")

# ── 세션 상태 ─────────────────────────────────────────────────────────────────
for k, v in {
    "generating": False,
    "result_b64": None,
    "sketch_b64": None,
    "sketch_hash": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

is_gen: bool = st.session_state.generating


def to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _file_b64(path: str, mime: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


_BASE = os.path.dirname(os.path.abspath(__file__))
_SAMPLES = os.path.join(_BASE, "animal_samples")
_EX_SKETCH   = f"data:image/jpeg;base64,{_file_b64(os.path.join(_SAMPLES, 'test_sketch 2.jpg'), 'jpeg')}"
_EX_EMOTICON = f"data:image/png;base64,{_file_b64(os.path.join(_SAMPLES, 'EX_emoticon.png'), 'png')}"


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700;900&display=swap');

/* ─ 배경: 연한 도트 그리드 종이 ─ */
.stApp {
    background-color: #faf8f3;
    background-image: radial-gradient(circle, #ccc8bf 1px, transparent 1px);
    background-size: 20px 20px;
    font-family: 'Caveat', cursive;
}
.main .block-container { padding-top: 1.2rem; max-width: 760px; }

/* ─ 사이드바 자동 페이지 네비 숨김 ─ */
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ─ 헤더 네비게이션 링크 ─ */
a[data-testid="stPageLink-NavLink"] {
    font-family: 'Caveat', cursive !important;
    font-size: 1.05rem !important; font-weight: 700 !important;
    background: white !important;
    border: 2px solid #222 !important;
    border-radius: 3px 5px 4px 3px / 4px 3px 5px 4px !important;
    padding: 7px 14px !important;
    box-shadow: 3px 3px 0 #222 !important;
    transition: transform .1s, box-shadow .1s, background .15s !important;
    display: flex !important; justify-content: center !important;
    text-decoration: none !important; color: #222 !important;
}
a[data-testid="stPageLink-NavLink"]:hover {
    background: #FFE835 !important;
    transform: translate(-1px,-1px) !important;
    box-shadow: 4px 4px 0 #222 !important;
}
a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #222 !important; color: white !important;
    box-shadow: 2px 2px 0 #555 !important;
}

/* ─ 헤더 카드 ─ */
.header-card {
    background: white;
    border: 2.5px solid #222;
    border-radius: 4px 8px 5px 7px / 7px 4px 8px 5px;
    padding: 20px 26px 16px;
    margin-bottom: 12px;
    box-shadow: 5px 5px 0 #222;
    transform: rotate(-0.3deg);
    position: relative;
    display: flex;
    align-items: center;
    gap: 18px;
}
.header-card::before {
    content: ''; position: absolute; top: -9px; left: 36px;
    width: 60px; height: 10px;
    background: rgba(255,230,50,.88); border: 1.5px solid #c8a200;
    border-radius: 2px;
}
.header-card::after {
    content: ''; position: absolute; top: -9px; right: 44px;
    width: 44px; height: 10px;
    background: rgba(255,230,50,.88); border: 1.5px solid #c8a200;
    border-radius: 2px;
}
.header-mascot {
    font-size: 4.2rem; line-height: 1; flex-shrink: 0;
    transform: rotate(-5deg);
    filter: drop-shadow(2px 2px 0 #e0d8c8);
}
.header-text { flex: 1; }
.h-tags { display: flex; gap: 7px; margin-bottom: 10px; flex-wrap: wrap; }
.h-tag  { font-family:'Caveat',cursive; font-size:.9rem; font-weight:700;
           padding:2px 10px; border:2px solid #222; border-radius:2px; }
.t-black  { background:#222; color:white; }
.t-yellow { background:#FFE835; color:#222; }
.t-pink   { background:#FF4081; color:white; }
.header-card h1 { font-family:'Caveat',cursive; font-size:2.5rem; font-weight:900;
    color:#222; margin:0 0 4px; line-height:1.05; }
.header-card .sub { font-family:'Caveat',cursive; font-size:1.15rem; color:#777; }

/* ─ 낙서 데코 라인 ─ */
.doodle-line { text-align:center; font-size:1rem; color:#d0cbbf;
    letter-spacing:8px; margin:8px 0 10px; font-family:'Caveat',cursive; }

/* ─ 컨셉 스트립 (가로 한 줄, 컴팩트) ─ */
.concept-strip {
    display: flex; align-items: center; justify-content: center; gap: 14px;
    background: white;
    border: 2.5px solid #222;
    border-radius: 5px 3px 6px 4px / 4px 6px 3px 5px;
    padding: 10px 22px;
    margin-bottom: 12px;
    box-shadow: 4px 4px 0 #222;
    transform: rotate(0.2deg);
}
.cs-side { text-align: center; }
.cs-lbl  { font-family:'Caveat',cursive; font-size:.78rem; font-weight:700;
    letter-spacing:1.5px; color:#aaa; margin-bottom:4px; text-transform:uppercase; }
.cs-icons-grey  { font-size:1.55rem; letter-spacing:4px;
    filter:grayscale(1); opacity:.45; }
.cs-icons-color { font-size:1.55rem; letter-spacing:4px; }
.cs-arrow { font-family:'Caveat',cursive; font-size:1.4rem; color:#222;
    font-weight:900; display:flex; flex-direction:column; align-items:center; line-height:1; }
.cs-arrow-sub { font-size:.72rem; color:#aaa; margin-top:2px;
    font-family:'Caveat',cursive; letter-spacing:1px; }

/* ─ 스케치북 업로드 ─ */
.sb-outer {
    position: relative;
    margin-bottom: 20px;
    transform: rotate(-0.3deg);
}
.sb-outer::before {
    content:''; position:absolute;
    bottom:-5px; left:6px; right:-6px; top:6px;
    background:#e0dcd0; border:2.5px solid #222;
    border-radius:2px 5px 5px 3px; z-index:0;
}
.sb-outer::after {
    content:''; position:absolute;
    bottom:-10px; left:12px; right:-12px; top:12px;
    background:#d2cec0; border:2.5px solid #222;
    border-radius:2px 5px 5px 3px; z-index:-1;
}
.sb-book {
    position:relative; z-index:1;
    border:2.5px solid #222;
    border-radius:3px 6px 5px 3px;
    box-shadow:5px 5px 0 #222;
    overflow:hidden;
}
.sb-spine {
    background:#f0ede5;
    border-bottom:2.5px solid #222;
    padding:5px 14px 0;
    display:flex; gap:8px; align-items:flex-end;
}
.sb-ring {
    width:18px; height:26px; flex-shrink:0;
    border:3px solid #222;
    border-radius:50% 50% 42% 42% / 55% 55% 45% 45%;
    background:white;
    position:relative; bottom:-3px;
    box-shadow:inset 0 -3px 0 rgba(0,0,0,.12);
}
.sb-page {
    background:
        linear-gradient(90deg, transparent 42px, rgba(220,80,80,.25) 42px, rgba(220,80,80,.25) 44px, transparent 44px),
        repeating-linear-gradient(transparent, transparent 27px, #c8dff5 27px, #c8dff5 28px),
        #fefdf8;
    padding:14px 20px 16px 52px;
    position:relative;
}
.sb-page-label {
    font-family:'Caveat',cursive; font-size:1.3rem; font-weight:700;
    color:#222; margin-bottom:10px;
}

/* ─ Streamlit 기본 실행 상태 위젯 숨김 ─ */
[data-testid="stStatusWidget"] { visibility: hidden !important; }

/* ─ 스케치북 이미지 디스플레이 (State B/C/D) ─ */
.sb-disp-outer {
    position:relative; margin:12px 0 16px; transform:rotate(0.12deg);
}
.sb-disp-outer::before {
    content:''; position:absolute;
    bottom:-5px; left:6px; right:-6px; top:6px;
    background:#e0dcd0; border:2.5px solid #222;
    border-radius:2px 5px 5px 3px; z-index:0;
}
.sb-disp-outer::after {
    content:''; position:absolute;
    bottom:-10px; left:12px; right:-12px; top:12px;
    background:#d2cec0; border:2.5px solid #222;
    border-radius:2px 5px 5px 3px; z-index:-1;
}
.sb-disp-book {
    position:relative; z-index:1;
    border:2.5px solid #222;
    border-radius:3px 6px 5px 3px;
    box-shadow:5px 5px 0 #222; overflow:hidden;
}
.sb-disp-page {
    background:
        linear-gradient(90deg, transparent 38px, rgba(220,80,80,.2) 38px, rgba(220,80,80,.2) 40px, transparent 40px),
        repeating-linear-gradient(transparent, transparent 27px, #c8dff5 27px, #c8dff5 28px),
        #fefdf8;
    padding:14px 18px 18px 46px;
}
.sb-photo-tape {
    width:50px; height:11px;
    background:rgba(255,230,50,.88); border:1.5px solid #c8a200;
    border-radius:2px; margin:0 auto 5px; transform:rotate(-2deg);
}
.sb-photo-tape.r { transform:rotate(2deg); }
.sb-photo-label {
    font-family:'Caveat',cursive; font-size:1.1rem; font-weight:700;
    text-align:center; margin-bottom:6px; color:#222;
}
.sb-photo-label.pink { color:#FF4081; }

[data-testid="stFileUploaderDropzone"] {
    background:rgba(255,255,255,.85) !important;
    border:2px dashed #aaa !important; border-radius:4px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color:#222 !important; background:rgba(255,255,255,.95) !important;
}
.upload-tip { background:#fffde7; border-left:3px solid #ffc107;
    padding:8px 12px; margin-top:10px;
    font-family:'Caveat',cursive; font-size:1rem; color:#5d4037; border-radius:2px; }

/* ─ 빈 슬롯 ─ */
.empty-slot {
    width:100%; aspect-ratio:1; background:#f7f5f0;
    border:2px dashed #ccc;
    border-radius:5px 3px 6px 4px / 4px 6px 3px 5px;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    font-family:'Caveat',cursive; color:#ccc; gap:6px;
}
.empty-slot .slot-icon { font-size:2.4rem; opacity:.4; }
.empty-slot .slot-txt  { font-size:1rem; }

/* ─ 변환 버튼 ─ */
div[data-testid="stButton"] > button {
    background:#222 !important; color:white !important;
    border:2.5px solid #222 !important;
    border-radius:4px 7px 5px 6px / 6px 4px 7px 5px !important;
    padding:10px 24px !important;
    font-family:'Caveat',cursive !important;
    font-size:1.3rem !important; font-weight:700 !important;
    box-shadow:4px 4px 0 #888 !important; width:100% !important;
    transition:transform .1s, box-shadow .1s, background .15s !important;
}
div[data-testid="stButton"] > button:hover {
    background:#FF4081 !important; border-color:#FF4081 !important;
    transform:translate(-2px,-2px) !important; box-shadow:6px 6px 0 #c8004a !important;
}

/* ─ 생성 중 애니메이션 ─ */
@keyframes sketch-pulse {
    0%   { filter:grayscale(1) blur(0px) saturate(0) brightness(1); }
    30%  { filter:grayscale(.5) blur(4px) saturate(2.5) brightness(1.1); }
    60%  { filter:grayscale(0) blur(7px) saturate(4) brightness(1.3) hue-rotate(20deg); }
    100% { filter:grayscale(1) blur(0px) saturate(0) brightness(1); }
}
.gen-img {
    animation:sketch-pulse 3s ease-in-out infinite;
    width:100%; display:block;
    border:2.5px solid #222;
    border-radius:4px 7px 5px 6px / 6px 4px 7px 5px;
}
@keyframes rise {
    0%   { transform:translateY(0) scale(.6) rotate(-5deg); opacity:0; }
    15%  { opacity:1; }
    100% { transform:translateY(-90px) scale(1.5) rotate(20deg); opacity:0; }
}
.fe  { position:absolute; font-size:1.8rem; pointer-events:none; }
.fe1 { left:8%;  bottom:5%; animation:rise 2.4s 0.0s ease-out infinite; }
.fe2 { left:43%; bottom:3%; animation:rise 2.4s 0.8s ease-out infinite; }
.fe3 { right:8%; bottom:5%; animation:rise 2.4s 1.6s ease-out infinite; }
@keyframes dot-pop {
    0%,100% { opacity:.2; transform:scale(1); }
    50%      { opacity:1;  transform:scale(1.5); }
}
.dp  { display:inline-block; animation:dot-pop 1.2s ease-in-out infinite; }
.dp2 { animation-delay:.4s; }
.dp3 { animation-delay:.8s; }

/* ─ 결과 레이블 ─ */
.rl   { font-family:'Caveat',cursive; font-size:1.4rem; font-weight:700;
    text-align:center; margin-bottom:7px; }
.rl-s { color:#222; }
.rl-e { color:#FF4081; }

/* ─ 다운로드 버튼 ─ */
.stDownloadButton > button {
    background:#222 !important; color:white !important;
    border:2.5px solid #222 !important;
    border-radius:4px 7px 5px 6px / 6px 4px 7px 5px !important;
    padding:10px 24px !important;
    font-family:'Caveat',cursive !important;
    font-size:1.2rem !important; font-weight:700 !important;
    box-shadow:4px 4px 0 #888 !important; width:100% !important;
    transition:transform .1s, box-shadow .1s !important;
}
.stDownloadButton > button:hover {
    transform:translate(-2px,-2px) !important; box-shadow:6px 6px 0 #555 !important;
    background:#FF4081 !important; border-color:#FF4081 !important;
}

/* ─ 사이드바 ─ */
section[data-testid="stSidebar"] > div { background:#fffef5; border-right:2.5px solid #222; }
.lock-banner {
    background:#FFE835; border:2px solid #222;
    border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:7px 12px; margin-bottom:10px; box-shadow:3px 3px 0 #222;
    font-family:'Caveat',cursive; font-size:1.05rem; font-weight:700; color:#222;
}
.param-box {
    background:white; border:2px solid #222;
    border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:8px 12px; margin:3px 0 11px; box-shadow:3px 3px 0 #222;
    font-family:'Caveat',cursive; font-size:.95rem; color:#333; line-height:1.5;
}
.param-box b { color:#FF4081; }
.param-box.dim { opacity:.4; }

/* ─ 예시 비포/에프터 스트립 ─ */
.ex-strip {
    border: 1.5px dashed #d0cbbf;
    border-radius: 4px;
    padding: 10px 12px 12px;
    margin-bottom: 14px;
    background: rgba(255,255,255,.55);
}
.ex-hint {
    font-family:'Caveat',cursive; font-size:.85rem; font-weight:700;
    color:#aaa; letter-spacing:1px; margin-bottom:10px; text-align:center;
}
.ex-row {
    display:flex; align-items:center; justify-content:center; gap:14px;
}
.ex-photo { display:flex; flex-direction:column; align-items:center; gap:3px; }
.ex-tape  {
    width:38px; height:9px;
    background:rgba(255,230,50,.88); border:1.5px solid #c8a200;
    border-radius:2px; transform:rotate(-2deg);
}
.ex-tape.r { transform:rotate(2deg); }
.ex-frame {
    width:90px; height:90px;
    border:2px solid #222; border-radius:3px;
    overflow:hidden; background:white;
}
.ex-frame img { width:100%; height:100%; object-fit:contain; }
.ex-frame.result { border-color:#FF4081; box-shadow:3px 3px 0 #FF4081; }
.ex-lbl {
    font-family:'Caveat',cursive; font-size:.82rem; font-weight:700;
    color:#888; text-align:center;
}
.ex-lbl.pink { color:#FF4081; }
.ex-arrow {
    font-family:'Caveat',cursive; font-size:1.3rem; font-weight:900;
    color:#aaa; text-align:center; line-height:1.2;
}
.ex-arrow span { font-size:.72rem; display:block; color:#bbb; }

/* ─ 페이지 접힘 구분선 (스케치북 페이지 연속) ─ */
.sb-fold {
    border: none;
    border-top: 2px dashed #c8c4bc;
    margin: 14px -20px 16px -52px;
    position: relative;
}
.sb-fold::after {
    content: 'next page ↓';
    position: absolute;
    right: 12px; top: -9px;
    font-family:'Caveat',cursive; font-size:.72rem;
    color:#bbb; background:#fefdf8; padding:0 5px;
}

/* ─ 푸터 ─ */
.doodle-footer { text-align:center; font-family:'Caveat',cursive;
    font-size:.95rem; color:#c0bab0; margin-top:28px; line-height:1.9; }
</style>
""", unsafe_allow_html=True)


# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <div class="header-mascot">🐱</div>
    <div class="header-text">
        <div class="h-tags">
            <div class="h-tag t-yellow">✏️ SKETCH</div>
            <div class="h-tag t-black">→</div>
            <div class="h-tag t-pink">😸 EMOTICON</div>
        </div>
        <h1>손그림 이모티콘 메이커</h1>
        <div class="sub">내 낙서가 귀여운 이모티콘으로 ✨</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 헤더 네비게이션 ──────────────────────────────────────────────────────────
nc1, nc2, nc3 = st.columns(3)
with nc1: st.page_link("app.py", label="✏️ 이모티콘 메이커", use_container_width=True)
with nc2: st.page_link("pages/01_학습_리포트.py", label="📊 학습 리포트", use_container_width=True)
with nc3: st.page_link("pages/02_그래프.py", label="📈 성능 그래프", use_container_width=True)

st.markdown('<div class="doodle-line">✏ ✦ ♡ ✦ ✏</div>', unsafe_allow_html=True)

# ── 컨셉 스트립 (가로 한 줄) ─────────────────────────────────────────────────
st.markdown("""
<div class="concept-strip">
    <div class="cs-side">
        <div class="cs-lbl">내 손그림</div>
        <div class="cs-icons-grey">🐱 🐶 🐻 🦊</div>
    </div>
    <div class="cs-arrow">
        ──✏──→
        <span class="cs-arrow-sub">AI 변환</span>
    </div>
    <div class="cs-side">
        <div class="cs-lbl" style="color:#FF4081;">이모티콘</div>
        <div class="cs-icons-color">😸 🐶 🧸 🦊</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── 사이드바 ──────────────────────────────────────────────────────────────────
pb = "param-box dim" if is_gen else "param-box"

with st.sidebar:
    st.markdown("## ✏️ 생성 설정")
    if is_gen:
        st.markdown('<div class="lock-banner">🔒 생성 중 — 설정 변경 불가</div>',
                    unsafe_allow_html=True)
    st.divider()

    st.markdown("**✨ 그림 완성 단계**")
    steps = st.slider("그림 완성 단계", 10, 50, 30, 5,
                      label_visibility="collapsed", disabled=is_gen, key="steps")
    st.markdown(f"""<div class="{pb}">
AI가 이모티콘을 얼마나 꼼꼼히 그릴지<br>
<b>↑ 높이면</b>: 더 세밀하게 (시간 오래)<br>
<b>↓ 낮추면</b>: 빠르지만 거칠 수 있어요<br>
🎯 추천: <b>20~30</b></div>""", unsafe_allow_html=True)

    st.markdown("**🎨 이모티콘 스타일 강도**")
    guidance = st.slider("이모티콘 스타일 강도", 5.0, 12.0, 7.5, 0.5,
                         label_visibility="collapsed", disabled=is_gen, key="guidance")
    st.markdown(f"""<div class="{pb}">
이모티콘 느낌을 얼마나 강하게 적용할지<br>
<b>↑ 높이면</b>: 이모티콘 스타일 강하게<br>
<b>↓ 낮추면</b>: 자연스럽고 자유로운 느낌<br>
🎯 추천: <b>7~9</b></div>""", unsafe_allow_html=True)

    st.markdown("**✏️ 손그림 반영 강도**")
    cn_scale = st.slider("손그림 반영 강도", 0.3, 1.2, 0.8, 0.1,
                         label_visibility="collapsed", disabled=is_gen, key="cn_scale")
    st.markdown(f"""<div class="{pb}">
내 손그림 선을 얼마나 따라갈지<br>
<b>↑ 높이면</b>: 내 선 모양 그대로<br>
<b>↓ 낮추면</b>: AI가 자유롭게 변형<br>
🎯 추천: <b>0.7~0.9</b></div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""**💡 잘 나오는 손그림**
- 흰/밝은 배경 + 검은 선
- 얼굴 위주 (전신 ❌)
- 선을 굵고 단순하게
""")


# ── 스케치북 (업로드 ~ 결과까지 하나의 페이지) ───────────────────────────────
_rings = '<div class="sb-ring"></div>' * 22
st.markdown(f"""
<div class="sb-outer">
  <div class="sb-book">
    <div class="sb-spine">{_rings}</div>
    <div class="sb-page">
      <div class="ex-strip">
        <div class="ex-hint">💡 예시 — 이런 손그림을 올려보세요</div>
        <div class="ex-row">
          <div class="ex-photo">
            <div class="ex-tape"></div>
            <div class="ex-frame">
              <img src="{_EX_SKETCH}"/>
            </div>
            <div class="ex-lbl">✏️ 손그림</div>
          </div>
          <div class="ex-arrow">→<span>AI 변환</span></div>
          <div class="ex-photo">
            <div class="ex-tape r"></div>
            <div class="ex-frame result">
              <img src="{_EX_EMOTICON}"/>
            </div>
            <div class="ex-lbl pink">😸 이모티콘</div>
          </div>
        </div>
      </div>
      <div class="sb-page-label">✏️ 손그림을 올려주세요</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "파일 선택", type=["jpg", "jpeg", "png"],
    label_visibility="collapsed", disabled=is_gen,
)
st.markdown("""
      <div class="upload-tip">
        ⚠️ 최초 1회만 모델 다운로드 (5~10분) · 이후 재시작 시 메모리 로드만 (30초~2분)
      </div>
""", unsafe_allow_html=True)

if uploaded:
    file_hash = hashlib.md5(uploaded.getvalue()).hexdigest()
    if st.session_state.sketch_hash != file_hash:
        st.session_state.sketch_hash = file_hash
        st.session_state.result_b64 = None
        st.session_state.sketch_b64 = None


# ── State B: 파일 업로드됨 ───────────────────────────────────────────────────
if uploaded and not is_gen and not st.session_state.result_b64:
    sketch = Image.open(io.BytesIO(uploaded.getvalue()))

    st.markdown('<div class="sb-fold"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sb-photo-tape"></div>'
                    '<div class="sb-photo-label">✏️ 내 손그림</div>', unsafe_allow_html=True)
        st.image(sketch, use_container_width=True)
    with col2:
        st.markdown('<div class="sb-photo-tape r"></div>'
                    '<div class="sb-photo-label pink">😸 여기에 변환돼요</div>', unsafe_allow_html=True)
        st.markdown("""<div class="empty-slot">
            <div class="slot-icon">🐾</div>
            <div class="slot-txt">변환 후 등장!</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("✏️ 이모티콘으로 변환하기!"):
            st.session_state.sketch_b64 = to_b64(sketch)
            st.session_state.generating = True
            st.session_state.result_b64 = None
            st.rerun()


# ── State C: 생성 중 ─────────────────────────────────────────────────────────
if is_gen and st.session_state.sketch_b64:
    b64 = st.session_state.sketch_b64
    gen_steps = st.session_state.get("steps", 30)

    st.markdown('<div class="sb-fold"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sb-photo-tape"></div>'
                    '<div class="sb-photo-label">✏️ 내 손그림</div>', unsafe_allow_html=True)
        st.markdown(
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width:100%;border:2.5px solid #222;'
            f'border-radius:4px 7px 5px 6px / 6px 4px 7px 5px;"/>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<div class="sb-photo-tape r"></div>'
                    '<div class="sb-photo-label pink">✨ 그리는 중...</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="position:relative;overflow:visible;">
    <img class="gen-img" src="data:image/png;base64,{b64}"/>
    <div class="fe fe1">✨</div>
    <div class="fe fe2">🎨</div>
    <div class="fe fe3">😸</div>
</div>
<div style="text-align:center;margin-top:10px;
    font-family:'Caveat',cursive;font-size:1.5rem;font-weight:700;color:#222;">
    ✏️ 그리는 중
    <span class="dp">.</span><span class="dp dp2">.</span><span class="dp dp3">.</span>
</div>
<div style="text-align:center;font-family:'Caveat',cursive;font-size:.9rem;color:#999;margin-top:2px;">
    {gen_steps} 스텝 · 잠깐만요!
</div>
""", unsafe_allow_html=True)

    sketch_img = Image.open(io.BytesIO(base64.b64decode(b64)))
    pipe = load_pipeline()
    result = convert_sketch(
        pipe, sketch_img,
        steps=st.session_state.get("steps", 30),
        guidance=st.session_state.get("guidance", 7.5),
        cn_scale=st.session_state.get("cn_scale", 0.8),
    )
    st.session_state.result_b64 = to_b64(result)
    st.session_state.generating = False
    st.rerun()


# ── State D: 결과 ────────────────────────────────────────────────────────────
if not is_gen and st.session_state.result_b64 and st.session_state.sketch_b64:
    s_b64 = st.session_state.sketch_b64
    r_b64 = st.session_state.result_b64

    st.markdown('<div class="sb-fold"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sb-photo-tape"></div>'
                    '<div class="sb-photo-label">✏️ 내 손그림</div>', unsafe_allow_html=True)
        st.markdown(
            f'<img src="data:image/png;base64,{s_b64}" '
            f'style="width:100%;border:2.5px solid #222;'
            f'border-radius:4px 7px 5px 6px / 6px 4px 7px 5px;'
            f'filter:grayscale(.1);"/>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<div class="sb-photo-tape r"></div>'
                    '<div class="sb-photo-label pink">😸 완성!</div>', unsafe_allow_html=True)
        st.markdown(
            f'<img src="data:image/png;base64,{r_b64}" '
            f'style="width:100%;border:2.5px solid #FF4081;'
            f'border-radius:4px 7px 5px 6px / 6px 4px 7px 5px;'
            f'box-shadow:4px 4px 0 #FF4081;"/>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.download_button(
            "⬇️  이모티콘 저장 (PNG)",
            base64.b64decode(r_b64),
            "emoticon.png", "image/png",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔄 다시 만들기"):
            st.session_state.result_b64 = None
            st.session_state.sketch_b64 = None
            st.session_state.sketch_hash = None
            st.rerun()

# ── 스케치북 닫기 ─────────────────────────────────────────────────────────────
st.markdown("""
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 푸터 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="doodle-footer">
    ✏️ ～ ♡ ～ 😸<br>
    손그림 이모티콘 메이커 · SD v1.5 + LoRA + ControlNet
</div>
""", unsafe_allow_html=True)
