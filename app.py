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
    "preview_b64": None,
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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

/* ─ 배경: 연한 도트 그리드 (책상) ─ */
.stApp {
    background-color: #f0ede5;
    background-image: radial-gradient(circle, #ccc8bf 1px, transparent 1px);
    background-size: 20px 20px;
    font-family: 'Noto Sans KR', sans-serif;
}

/* ─ 메인 컨텐츠 블록 = 스케치북 한 페이지 ─ */
.main .block-container {
    background:
        linear-gradient(90deg, transparent 42px, rgba(220,80,80,.18) 42px, rgba(220,80,80,.18) 44px, transparent 44px),
        repeating-linear-gradient(transparent, transparent 27px, #c8dff5 27px, #c8dff5 28px),
        #fefdf8;
    border: 2.5px solid #222 !important;
    border-radius: 4px 8px 6px 4px;
    box-shadow: 8px 8px 0 #d0cbbf, 15px 15px 0 #e8e4da;
    padding: 0 24px 32px 60px !important;
    max-width: 760px !important;
    margin-top: 20px !important;
}

/* ─ 스케치북 상단 링 바인딩 ─ */
.sb-global-spine {
    margin: 0 -24px 24px -60px;
    background: #f0ede5;
    border-bottom: 2.5px solid #222;
    padding: 6px 14px 0;
    display: flex; gap: 8px; align-items: flex-end;
}

/* ─ 사이드바 자동 페이지 네비 숨김 ─ */
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ─ 헤더 네비게이션 링크 ─ */
a[data-testid="stPageLink-NavLink"] {
    font-family: 'Noto Sans KR', sans-serif !important;
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
.h-tag  { font-family:'Noto Sans KR', sans-serif; font-size:.9rem; font-weight:700;
           padding:2px 10px; border:2px solid #222; border-radius:2px; }
.t-black  { background:#222; color:white; }
.t-yellow { background:#FFE835; color:#222; }
.t-pink   { background:#FF4081; color:white; }
.header-card h1 { font-family:'Noto Sans KR', sans-serif; font-size:2.5rem; font-weight:900;
    color:#222; margin:0 0 4px; line-height:1.05; }
.header-card .sub { font-family:'Noto Sans KR', sans-serif; font-size:1.15rem; color:#777; }

/* ─ 낙서 데코 라인 ─ */
.doodle-line { text-align:center; font-size:1rem; color:#d0cbbf;
    letter-spacing:8px; margin:8px 0 10px; font-family:'Noto Sans KR', sans-serif; }

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
.cs-lbl  { font-family:'Noto Sans KR', sans-serif; font-size:.78rem; font-weight:700;
    letter-spacing:1.5px; color:#aaa; margin-bottom:4px; text-transform:uppercase; }
.cs-icons-grey  { font-size:1.55rem; letter-spacing:4px;
    filter:grayscale(1); opacity:.45; }
.cs-icons-color { font-size:1.55rem; letter-spacing:4px; }
.cs-arrow { font-family:'Noto Sans KR', sans-serif; font-size:1.4rem; color:#222;
    font-weight:900; display:flex; flex-direction:column; align-items:center; line-height:1; }
.cs-arrow-sub { font-size:.72rem; color:#aaa; margin-top:2px;
    font-family:'Noto Sans KR', sans-serif; letter-spacing:1px; }

/* ─ 스케치북 링 ─ */
.sb-ring {
    width:18px; height:26px; flex-shrink:0;
    border:3px solid #222;
    border-radius:50% 50% 42% 42% / 55% 55% 45% 45%;
    background:white;
    position:relative; bottom:-3px;
    box-shadow:inset 0 -3px 0 rgba(0,0,0,.12);
}
.sb-page-label {
    font-family:'Noto Sans KR', sans-serif; font-size:1.3rem; font-weight:700;
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
    font-family:'Noto Sans KR', sans-serif; font-size:1.1rem; font-weight:700;
    text-align:center; margin-bottom:6px; color:#222;
}
.sb-photo-label.pink { color:#FF4081; }

[data-testid="stFileUploaderDropzone"] {
    background:rgba(255,255,255,.7) !important;
    border:2.5px dashed #bbb !important;
    border-radius:6px !important;
    min-height:100px !important;
    display:flex !important; align-items:center !important; justify-content:center !important;
    transition:border-color .2s, background .2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploaderDropzone"]:focus-within {
    border-color:#222 !important;
    background:rgba(255,255,255,.95) !important;
    border-style:solid !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    font-family:'Noto Sans KR', sans-serif !important;
    font-size:1.1rem !important; color:#888 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    font-family:'Noto Sans KR', sans-serif !important;
    font-size:0.9rem !important;
}
.upload-tip { background:#fffde7; border-left:3px solid #ffc107;
    padding:8px 12px; margin-top:10px;
    font-family:'Noto Sans KR', sans-serif; font-size:1rem; color:#5d4037; border-radius:2px; }

/* ─ 빈 슬롯 ─ */
.empty-slot {
    width:100%; aspect-ratio:1; background:#f7f5f0;
    border:2px dashed #ccc;
    border-radius:5px 3px 6px 4px / 4px 6px 3px 5px;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    font-family:'Noto Sans KR', sans-serif; color:#ccc; gap:6px;
}
.empty-slot .slot-icon { font-size:2.4rem; opacity:.4; }
.empty-slot .slot-txt  { font-size:1rem; }

/* ─ 변환 버튼 ─ */
div[data-testid="stButton"] > button {
    background:#222 !important; color:white !important;
    border:2.5px solid #222 !important;
    border-radius:4px 7px 5px 6px / 6px 4px 7px 5px !important;
    padding:10px 24px !important;
    font-family:'Noto Sans KR', sans-serif !important;
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
    100% { transform:translateY(-180px) scale(1.5) rotate(20deg); opacity:0; }
}
.fe  { position:absolute; font-size:2.2rem; pointer-events:none; }
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
.rl   { font-family:'Noto Sans KR', sans-serif; font-size:1.4rem; font-weight:700;
    text-align:center; margin-bottom:7px; }
.rl-s { color:#222; }
.rl-e { color:#FF4081; }

/* ─ 다운로드 버튼 ─ */
.stDownloadButton > button {
    background:#222 !important; color:white !important;
    border:2.5px solid #222 !important;
    border-radius:4px 7px 5px 6px / 6px 4px 7px 5px !important;
    padding:10px 24px !important;
    font-family:'Noto Sans KR', sans-serif !important;
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
    font-family:'Noto Sans KR', sans-serif; font-size:1.05rem; font-weight:700; color:#222;
}
.param-box {
    background:white; border:2px solid #222;
    border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:8px 12px; margin:3px 0 11px; box-shadow:3px 3px 0 #222;
    font-family:'Noto Sans KR', sans-serif; font-size:.95rem; color:#333; line-height:1.5;
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
    font-family:'Noto Sans KR', sans-serif; font-size:.85rem; font-weight:700;
    color:#aaa; letter-spacing:1px; margin-bottom:10px; text-align:center;
}
.ex-row {
    display:flex; align-items:center; justify-content:center; gap:14px;
}
.ex-photo { display:flex; flex-direction:column; align-items:center; gap:3px; }
.ex-tape  {
    width:60px; height:11px;
    background:rgba(255,230,50,.88); border:1.5px solid #c8a200;
    border-radius:2px; transform:rotate(-2deg);
}
.ex-tape.r { transform:rotate(2deg); }
.ex-frame {
    width:220px; height:220px;
    border:2.5px solid #222; border-radius:4px 7px 5px 6px / 6px 4px 7px 5px;
    overflow:hidden; background:white;
    box-shadow:4px 4px 0 #e0dcd0;
}
.ex-frame img { width:100%; height:100%; object-fit:contain; }
.ex-frame.result { border-color:#FF4081; box-shadow:4px 4px 0 #FF4081; }
.ex-lbl {
    font-family:'Noto Sans KR', sans-serif; font-size:1.05rem; font-weight:700;
    color:#888; text-align:center; margin-top:2px;
}
.ex-lbl.pink { color:#FF4081; }
.ex-arrow {
    font-family:'Noto Sans KR', sans-serif; font-size:1.6rem; font-weight:900;
    color:#aaa; text-align:center; line-height:1.2; padding:0 8px;
}
.ex-arrow span { font-size:.85rem; display:block; color:#bbb; }

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
    font-family:'Noto Sans KR', sans-serif; font-size:.72rem;
    color:#bbb; background:#fefdf8; padding:0 5px;
}

/* ─ 푸터 ─ */
.doodle-footer { text-align:center; font-family:'Noto Sans KR', sans-serif;
    font-size:.95rem; color:#c0bab0; margin-top:28px; line-height:1.9; }
</style>
""", unsafe_allow_html=True)


# ── 전역 스케치북 링 (페이지 상단) ────────────────────────────────────────────
_rings_g = '<div class="sb-ring"></div>' * 26
st.markdown(f'<div class="sb-global-spine">{_rings_g}</div>', unsafe_allow_html=True)

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
with nc1: st.page_link("app.py",                      label="✏️ 이모티콘 메이커", use_container_width=True)
with nc2: st.page_link("pages/01_학습_리포트.py",     label="📊 학습 리포트",     use_container_width=True)
with nc3: st.page_link("pages/02_그래프.py",          label="📈 성능 그래프",     use_container_width=True)
nr1, nr2, nr3 = st.columns(3)
with nr1: st.page_link("pages/03_EDA_데이터분석.py", label="🔍 데이터 분석",     use_container_width=True)
with nr2: st.page_link("pages/04_가중치분석.py",      label="⚖️ 가중치 분석",    use_container_width=True)
with nr3: st.page_link("pages/05_생성품질.py",        label="🖼️ 생성 품질",      use_container_width=True)

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


# ── 동적 스트립 콘텐츠 결정 ──────────────────────────────────────────────────
_preview    = st.session_state.preview_b64
_sketch     = st.session_state.sketch_b64
_result     = st.session_state.result_b64
_gen_steps  = st.session_state.get("steps", 30)

if is_gen and _sketch:
    _hint       = f"✏️ AI가 이모티콘을 그리는 중 ({_gen_steps}스텝)..."
    _left_img   = f'<img src="data:image/png;base64,{_sketch}"/>'
    _left_lbl   = '✏️ 내 손그림'
    _left_sty   = ''
    _right_inner= (
        f'<img class="gen-img" src="data:image/png;base64,{_sketch}"/>'
        f'<div class="fe fe1">✨</div>'
        f'<div class="fe fe2">🎨</div>'
        f'<div class="fe fe3">😸</div>'
    )
    _right_lbl  = '✨ 그리는 중...'
    _right_sty  = 'color:#FF4081;'
    _right_fcls = 'ex-frame result'
    _right_fattr= 'style="overflow:visible;position:relative;"'
elif not is_gen and _result and _sketch:
    _hint       = '✨ 완성! 저장하거나 다시 만들어보세요'
    _left_img   = f'<img src="data:image/png;base64,{_sketch}"/>'
    _left_lbl   = '✏️ 내 손그림'
    _left_sty   = ''
    _right_inner= f'<img src="data:image/png;base64,{_result}"/>'
    _right_lbl  = '😸 완성!'
    _right_sty  = 'color:#FF4081;font-weight:900;'
    _right_fcls = 'ex-frame result'
    _right_fattr= ''
elif _preview:
    _hint       = '👆 변환 버튼을 눌러 이모티콘으로 만들어보세요'
    _left_img   = f'<img src="data:image/png;base64,{_preview}"/>'
    _left_lbl   = '✏️ 내 손그림'
    _left_sty   = ''
    _right_inner= f'<img src="{_EX_EMOTICON}" style="opacity:.3;"/>'
    _right_lbl  = '😸 여기에 생겨요'
    _right_sty  = 'color:#ccc;'
    _right_fcls = 'ex-frame result'
    _right_fattr= ''
else:
    _hint       = '💡 예시 — 이런 손그림을 올려보세요'
    _left_img   = f'<img src="{_EX_SKETCH}" style="opacity:.5;"/>'
    _left_lbl   = '✏️ 예시'
    _left_sty   = 'color:#aaa;'
    _right_inner= f'<img src="{_EX_EMOTICON}" style="opacity:.5;"/>'
    _right_lbl  = '😸 예시'
    _right_sty  = 'color:#aaa;'
    _right_fcls = 'ex-frame result'
    _right_fattr= ''

# ── 예시 / 결과 스트립 ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ex-strip">
  <div class="ex-hint">{_hint}</div>
  <div class="ex-row">
    <div class="ex-photo">
      <div class="ex-tape"></div>
      <div class="ex-frame">{_left_img}</div>
      <div class="ex-lbl" style="{_left_sty}">{_left_lbl}</div>
    </div>
    <div class="ex-arrow">→<span>AI 변환</span></div>
    <div class="ex-photo">
      <div class="ex-tape r"></div>
      <div class="{_right_fcls}" {_right_fattr}>{_right_inner}</div>
      <div class="ex-lbl" style="{_right_sty}">{_right_lbl}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 액션 버튼: 항상 업로드 라벨 위 ────────────────────────────────────────────
if _preview and not is_gen and not _result:
    c_left, c_mid, c_right = st.columns([5, 2, 5])
    with c_right:
        if st.button("✏️ 이모티콘으로 변환하기!", use_container_width=True):
            st.session_state.sketch_b64  = _preview
            st.session_state.generating  = True
            st.session_state.result_b64  = None
            st.rerun()

if not is_gen and _result:
    c_left, c_mid, c_right = st.columns([5, 2, 5])
    with c_right:
        st.download_button(
            "⬇️ 이모티콘 저장 (PNG)",
            base64.b64decode(_result),
            "emoticon.png", "image/png",
            use_container_width=True,
        )
        if st.button("🔄 다시 만들기", use_container_width=True):
            st.session_state.result_b64  = None
            st.session_state.sketch_b64  = None
            st.rerun()

st.markdown("""
      <div class="sb-page-label">✏️ 손그림을 올려주세요 (또는 여기에 드래그)</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "파일 선택", type=["jpg", "jpeg", "png"],
    label_visibility="collapsed", disabled=is_gen,
)

# 업로드 시 preview_b64 즉시 저장 → 스트립 업데이트
if uploaded:
    file_hash = hashlib.md5(uploaded.getvalue()).hexdigest()
    if st.session_state.sketch_hash != file_hash:
        st.session_state.sketch_hash  = file_hash
        st.session_state.result_b64   = None
        st.session_state.sketch_b64   = None
        st.session_state.preview_b64  = to_b64(Image.open(io.BytesIO(uploaded.getvalue())))
        st.rerun()
    elif not st.session_state.preview_b64:
        st.session_state.preview_b64  = to_b64(Image.open(io.BytesIO(uploaded.getvalue())))
        st.rerun()

st.markdown("""
      <div class="upload-tip">
        ⚠️ 최초 1회만 모델 다운로드 (5~10분) · 이후 재시작 시 메모리 로드만 (30초~2분)
      </div>
""", unsafe_allow_html=True)

# State C: 생성 실행
if is_gen and _sketch:
    _pipe   = load_pipeline()
    _img_in = Image.open(io.BytesIO(base64.b64decode(_sketch)))
    _img_out = convert_sketch(
        _pipe, _img_in,
        steps    = st.session_state.get("steps", 30),
        guidance = st.session_state.get("guidance", 7.5),
        cn_scale = st.session_state.get("cn_scale", 0.8),
    )
    st.session_state.result_b64  = to_b64(_img_out)
    st.session_state.generating  = False
    st.rerun()


# ── 푸터 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="doodle-footer">
    ✏️ ～ ♡ ～ 😸<br>
    손그림 이모티콘 메이커 · SD v1.5 + LoRA + ControlNet
</div>
""", unsafe_allow_html=True)
