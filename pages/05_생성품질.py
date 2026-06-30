import os
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.rcParams.update({'font.family': 'AppleGothic', 'axes.unicode_minus': False})
import numpy as np
from PIL import Image

st.set_page_config(page_title="생성 품질", page_icon="🖼️", layout="centered",
                   initial_sidebar_state="collapsed")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
.stApp {
    background-color: #faf8f3;
    background-image: radial-gradient(circle, #ccc8bf 1px, transparent 1px);
    background-size: 20px 20px; font-family: 'Noto Sans KR', sans-serif;
}
.main .block-container { padding-top: 1.2rem; max-width: 860px; }
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
a[data-testid="stPageLink-NavLink"] {
    font-family: 'Noto Sans KR', sans-serif !important; font-size: 1.0rem !important;
    font-weight: 700 !important; background: white !important;
    border: 2px solid #222 !important;
    border-radius: 3px 5px 4px 3px / 4px 3px 5px 4px !important;
    padding: 6px 10px !important; box-shadow: 3px 3px 0 #222 !important;
    transition: transform .1s, box-shadow .1s, background .15s !important;
    display: flex !important; justify-content: center !important;
    text-decoration: none !important; color: #222 !important;
}
a[data-testid="stPageLink-NavLink"]:hover {
    background: #FFE835 !important; transform: translate(-1px,-1px) !important;
    box-shadow: 4px 4px 0 #222 !important;
}
a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #222 !important; color: white !important; box-shadow: 2px 2px 0 #555 !important;
}
.header-card {
    background: white; border: 2.5px solid #222;
    border-radius: 4px 8px 5px 7px / 7px 4px 8px 5px;
    padding: 20px 26px 16px; margin-bottom: 14px;
    box-shadow: 5px 5px 0 #222; transform: rotate(-0.3deg);
    position: relative; display: flex; align-items: center; gap: 18px;
}
.header-card::before { content:''; position:absolute; top:-9px; left:36px;
    width:60px; height:10px; background:rgba(255,230,50,.88);
    border:1.5px solid #c8a200; border-radius:2px; }
.header-mascot { font-size:3.8rem; flex-shrink:0; transform:rotate(-5deg); }
.header-card h1 { font-family:'Noto Sans KR', sans-serif; font-size:2.3rem; font-weight:900; color:#222; margin:0 0 4px; }
.header-card .sub { font-family:'Noto Sans KR', sans-serif; font-size:1.1rem; color:#777; }
.doodle-line { text-align:center; font-size:1rem; color:#d0cbbf; letter-spacing:8px; margin:6px 0 12px; }
.section-card { background: white; border: 2.5px solid #222;
    border-radius: 5px 3px 6px 4px / 4px 6px 3px 5px;
    padding: 20px 24px; margin-bottom: 16px; box-shadow: 5px 5px 0 #222; }
.section-card.r2 { transform: rotate(-0.2deg); }
.section-card h2 { font-family:'Noto Sans KR', sans-serif; font-size:1.7rem; font-weight:900;
    color:#222; margin:0 0 14px; border-bottom:2px dashed #ccc; padding-bottom:8px; }
.epoch-label { font-family:'Noto Sans KR', sans-serif; font-size:.9rem; font-weight:700;
    text-align:center; margin-top:4px; }
.epoch-badge { font-family:'Noto Sans KR', sans-serif; font-size:.72rem; text-align:center;
    margin-top:2px; padding:2px 5px; border-radius:3px; display:inline-block;
    width:100%; border:1px solid #ccc; }
.info-box { font-family:'Noto Sans KR', sans-serif; font-size:.95rem; color:#555;
    margin-top:10px; padding:10px 14px; background:#fff9c4;
    border-left:3px solid #ffc107; border-radius:2px; line-height:1.6; }
.footer { text-align:center; font-family:'Noto Sans KR', sans-serif; font-size:.9rem;
    color:#c0bab0; margin-top:28px; line-height:1.9; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <div class="header-mascot">🖼️</div>
    <div>
        <h1>생성 품질 분석</h1>
        <div class="sub">전체 Epoch 이미지 그리드 · 이미지 통계 변화</div>
    </div>
</div>
<div class="doodle-line">✏ ✦ 🎨 ✦ ✏</div>
""", unsafe_allow_html=True)

# ── 네비게이션 ────────────────────────────────────────────────────────────────
r1a, r1b, r1c = st.columns(3)
with r1a: st.page_link("app.py",                      label="✏️ 이모티콘 메이커", use_container_width=True)
with r1b: st.page_link("pages/01_학습_리포트.py",     label="📊 학습 리포트",     use_container_width=True)
with r1c: st.page_link("pages/02_그래프.py",          label="📈 성능 그래프",     use_container_width=True)
r2a, r2b, r2c = st.columns(3)
with r2a: st.page_link("pages/03_EDA_데이터분석.py", label="🔍 데이터 분석",     use_container_width=True)
with r2b: st.page_link("pages/04_가중치분석.py",      label="⚖️ 가중치 분석",    use_container_width=True)
with r2c: st.page_link("pages/05_생성품질.py",        label="🖼️ 생성 품질",      use_container_width=True)

# ── 데이터 ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_DIR = os.path.join(BASE_DIR, "animal_samples")

EPOCH_INFO = [
    ("epoch_0_baseline.png", "Epoch 0",    "학습 전 기준선",    "#f0f0f0", False),
    ("epoch_1.png",          "Epoch 1",    "❌ 얼굴 콜라주",    "#ffcdd2", False),
    ("epoch_2.png",          "Epoch 2",    "흐릿한 실루엣",     "#fff9c4", False),
    ("epoch_3.png",          "Epoch 3",    "흑백 타일 패턴",    "#fff9c4", False),
    ("epoch_4.png",          "Epoch 4",    "형태 안정화",       "#fff9c4", False),
    ("epoch_5.png",          "Epoch 5",    "단일화, 채색 없음", "#fff9c4", False),
    ("epoch_6.png",          "Epoch 6",    "Loss 최솟값",       "#e8f5e9", False),
    ("epoch_7.png",          "Epoch 7 ✅", "✨ 최적 채택",      "#fce4ec", True ),
    ("epoch_8.png",          "Epoch 8",    "과적합 시작",       "#fff9c4", False),
    ("epoch_9.png",          "Epoch 9",    "배경 색상 이상",    "#e8f5e9", False),
    ("epoch_10.png",         "Epoch 10",   "❌ 과적합",         "#ffcdd2", False),
]

@st.cache_data
def compute_stats(samples_dir, fnames):
    out = {}
    for fname in fnames:
        path = os.path.join(samples_dir, fname)
        if not os.path.exists(path):
            continue
        arr = np.array(Image.open(path).convert("RGB"), dtype=float) / 255.0
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        maxc = np.maximum(np.maximum(r, g), b)
        minc = np.minimum(np.minimum(r, g), b)
        out[fname] = {
            "brightness":   float(arr.mean()),
            "saturation":   float(((maxc - minc) / (maxc + 1e-6)).mean()),
            "colorfulness": float(arr.std()),
        }
    return out

stats = compute_stats(SAMPLES_DIR, [ei[0] for ei in EPOCH_INFO])

# ── 섹션 1: 전체 Epoch 이미지 그리드 ────────────────────────────────────────
st.markdown('<div class="section-card"><h2>🖼️ 전체 Epoch 생성 이미지 비교</h2>', unsafe_allow_html=True)

COLS = 4
for row_i in range((len(EPOCH_INFO) + COLS - 1) // COLS):
    items = EPOCH_INFO[row_i * COLS : (row_i + 1) * COLS]
    cols  = st.columns(COLS)
    for col, (fname, label, badge, color, is_best) in zip(cols, items):
        path = os.path.join(SAMPLES_DIR, fname)
        with col:
            if os.path.exists(path):
                st.image(Image.open(path), use_container_width=True)
            lc = "#FF4081" if is_best else "#222"
            st.markdown(
                f'<div class="epoch-label" style="color:{lc};">{label}</div>'
                f'<div class="epoch-badge" style="background:{color};">{badge}</div>',
                unsafe_allow_html=True,
            )

st.markdown("""
<div class="info-box" style="margin-top:14px;">
💡 Epoch 0 = 학습 전 SD v1.5 기본 생성 이미지.
학습이 진행되면서 Twemoji 스타일로 수렴하고 Epoch 7에서 최적 품질 달성.
Epoch 9~10에서 과적합으로 배경 노이즈 및 스타일 붕괴 관찰.
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 2: 이미지 통계 변화 ─────────────────────────────────────────────────
st.markdown('<div class="section-card r2"><h2>📊 Epoch별 이미지 통계 변화</h2>', unsafe_allow_html=True)

ep_labels, brightness_list, saturation_list, colorfulness_list = [], [], [], []
best_idx = 0
for i, (fname, label, *_) in enumerate(EPOCH_INFO):
    if fname not in stats:
        continue
    ep_labels.append(label.replace(" ✅", ""))
    brightness_list.append(stats[fname]["brightness"])
    saturation_list.append(stats[fname]["saturation"])
    colorfulness_list.append(stats[fname]["colorfulness"])
    if "✅" in label:
        best_idx = len(ep_labels) - 1

x = np.arange(len(ep_labels))
fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
fig.patch.set_facecolor("#faf8f3")

plot_data = [
    (brightness_list,   "밝기 (Brightness)",          "#888",   "평균 픽셀 밝기 (0=검정, 1=흰색)"),
    (saturation_list,   "채도 (Saturation)",           "#FF4081","HSV 채도 평균 (높을수록 선명)"),
    (colorfulness_list, "색 다양성 (Colorfulness)",    "#222",   "RGB 표준편차 (높을수록 다채로움)"),
]

for ax, (vals, title, color, ylabel) in zip(axes, plot_data):
    ax.set_facecolor("#faf8f3")
    ax.plot(x, vals, color=color, linewidth=2.5,
            marker="o", markersize=7, markerfacecolor="white", markeredgewidth=2.5, zorder=3)
    ax.fill_between(x, vals, alpha=0.08, color=color)
    ax.scatter([best_idx], [vals[best_idx]], s=200, color="#FF4081", zorder=4)
    ax.axvline(x=best_idx, color="#FF4081", linestyle="--", linewidth=1.2, alpha=0.5)
    ax.set_title(title, fontsize=11, pad=6)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.3, color="#ccc")
    for sp in ax.spines.values(): sp.set_linewidth(1.3); sp.set_color("#222")

axes[-1].set_xticks(x)
axes[-1].set_xticklabels(ep_labels, rotation=20, ha="right", fontsize=9)
axes[-1].set_xlabel("Epoch", fontsize=11)
best_patch = mpatches.Patch(color="#FF4081", label="Epoch 7 최종 채택 ✅")
fig.legend(handles=[best_patch], loc="upper right", fontsize=10,
           framealpha=0.9, edgecolor="#222")
plt.tight_layout(rect=[0, 0, 1, 0.97])
st.pyplot(fig); plt.close(fig)

st.markdown("""
<div class="info-box">
📌 <b>밝기</b>: 초반 어두워졌다가 Epoch 5~7에서 안정화 → 흰 배경 + 단일 이모티콘 스타일로 수렴.<br>
📌 <b>채도</b>: Epoch 7 근방 피크 → Twemoji 특유의 선명한 색상이 학습됨.<br>
📌 <b>색 다양성</b>: Epoch 9~10에서 급증 → 과적합으로 배경 노이즈·색 혼합 발생.
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 3: 최적 Epoch 근거 요약표 ──────────────────────────────────────────
st.markdown('<div class="section-card"><h2>🏆 Epoch 6 vs 7 — 최적 선택 근거</h2>', unsafe_allow_html=True)

loss_by_epoch = {
    "epoch_1.png": 0.0446, "epoch_2.png": 0.0385, "epoch_3.png": 0.0416,
    "epoch_4.png": 0.0430, "epoch_5.png": 0.0454, "epoch_6.png": 0.0383,
    "epoch_7.png": 0.0427, "epoch_8.png": 0.0430, "epoch_9.png": 0.0420,
}

def fmt(fname, key):
    s = stats.get(fname, {})
    return f"{s[key]:.3f}" if key in s else "-"

rows = [
    ("Avg Loss (MSE)",       f"{loss_by_epoch.get('epoch_6.png','-'):.4f}",
                              f"{loss_by_epoch.get('epoch_7.png','-'):.4f}",
                              "Epoch 6 우위", "수치상 최솟값"),
    ("밝기",                 fmt("epoch_6.png","brightness"), fmt("epoch_7.png","brightness"),
                              "유사", "큰 차이 없음"),
    ("채도",                 fmt("epoch_6.png","saturation"), fmt("epoch_7.png","saturation"),
                              "Epoch 7 우위", "색상 선명도"),
    ("색 다양성",            fmt("epoch_6.png","colorfulness"), fmt("epoch_7.png","colorfulness"),
                              "유사", "큰 차이 없음"),
    ("시각 품질 (사람 평가)","흐릿함", "✨ 선명 + 스타일", "Epoch 7 우위 ✅", "최종 채택 기준"),
]

th = "background:#222;color:white;padding:7px 10px;border:2px solid #222;text-align:left;"
td = "padding:7px 10px;border:1.5px solid #ddd;font-family:'Noto Sans KR', sans-serif;font-size:.95rem;"
tda = td + "background:#f9f7f2;"

ths = f'<th style="{th}">지표</th><th style="{th}">Epoch 6</th><th style="{th}">Epoch 7</th><th style="{th}">우위</th><th style="{th}">비고</th>'
trs = "".join(
    f'<tr>{"".join(f"<td style=\"{td if i%2==0 else tda}\">{c}</td>" for c in row)}</tr>'
    for i, row in enumerate(rows)
)
st.markdown(f"""
<table style="width:100%;border-collapse:collapse;">
<tr>{ths}</tr>{trs}
</table>
<div class="info-box" style="margin-top:12px;">
🎯 Epoch 6이 Loss 수치 최솟값이지만 생성 이미지가 흐릿함.
Epoch 7은 Loss가 약간 높지만 단일 얼굴·채도·Twemoji 스타일 세 기준을 모두 만족 → <b>최종 채택</b>.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">✏️ ～ 🖼️ ～ 😸 · 생성 품질 분석 · SD v1.5 + LoRA</div>',
            unsafe_allow_html=True)
