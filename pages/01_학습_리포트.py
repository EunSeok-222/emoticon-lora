import os
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams.update({'font.family': 'AppleGothic', 'axes.unicode_minus': False})
from PIL import Image

st.set_page_config(page_title="학습 리포트", page_icon="📊", layout="centered",
                   initial_sidebar_state="collapsed")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_DIR = os.path.join(BASE_DIR, "animal_samples")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

.stApp {
    background-color: #faf8f3;
    background-image: radial-gradient(circle, #ccc8bf 1px, transparent 1px);
    background-size: 20px 20px;
    font-family: 'Noto Sans KR', sans-serif;
}
.main .block-container { padding-top: 1.2rem; max-width: 820px; }

[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }

[data-testid="collapsedControl"] { display: none !important; }

a[data-testid="stPageLink-NavLink"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 1.05rem !important; font-weight: 700 !important;
    background: white !important; border: 2px solid #222 !important;
    border-radius: 3px 5px 4px 3px / 4px 3px 5px 4px !important;
    padding: 7px 14px !important; box-shadow: 3px 3px 0 #222 !important;
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
.header-card::before {
    content:''; position:absolute; top:-9px; left:36px;
    width:60px; height:10px;
    background:rgba(255,230,50,.88); border:1.5px solid #c8a200; border-radius:2px;
}
.header-mascot { font-size:3.8rem; flex-shrink:0; transform:rotate(-5deg); }
.header-card h1 { font-family:'Noto Sans KR', sans-serif; font-size:2.3rem; font-weight:900; color:#222; margin:0 0 4px; }
.header-card .sub { font-family:'Noto Sans KR', sans-serif; font-size:1.1rem; color:#777; }
.doodle-line { text-align:center; font-size:1rem; color:#d0cbbf; letter-spacing:8px; margin:6px 0 12px; }

.section-card {
    background: white; border: 2.5px solid #222;
    border-radius: 5px 3px 6px 4px / 4px 6px 3px 5px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 5px 5px 0 #222;
}
.section-card.r2 { transform: rotate(-0.2deg); }
.section-card h2 { font-family:'Noto Sans KR', sans-serif; font-size:1.7rem; font-weight:900;
    color:#222; margin:0 0 14px; border-bottom:2px dashed #ccc; padding-bottom:8px; }

.compare-table { width:100%; border-collapse:collapse; font-family:'Noto Sans KR', sans-serif; font-size:1.05rem; }
.compare-table th { background:#222; color:white; padding:8px 14px; border:2px solid #222; text-align:left; }
.compare-table td { padding:8px 14px; border:2px solid #ddd; vertical-align:top; line-height:1.4; }
.compare-table tr:nth-child(even) td { background:#f9f7f2; }
.good { color:#FF4081; font-weight:700; }
.bad  { color:#aaa; }

.point-row { display:flex; gap:10px; margin-top:12px; flex-wrap:wrap; }
.point-card { flex:1; min-width:160px; background:#fffde7;
    border:2px solid #222; border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:12px 14px; box-shadow:3px 3px 0 #222; }
.point-card .pt { font-family:'Noto Sans KR', sans-serif; font-size:.78rem; font-weight:700;
    letter-spacing:1.5px; color:#999; margin-bottom:6px; text-transform:uppercase; }
.point-card .pv { font-family:'Noto Sans KR', sans-serif; font-size:1rem; color:#222; line-height:1.45; }
.point-card .pv b { color:#FF4081; }

.timeline { display:flex; align-items:flex-start; margin-top:8px; gap:0; }
.tl-item { flex:1; text-align:center; position:relative; }
.tl-line { position:absolute; top:8px; left:50%; right:-50%; height:3px; background:#222; z-index:0; }
.tl-item:last-child .tl-line { display:none; }
.tl-dot { width:18px; height:18px; border-radius:50%; border:3px solid #222;
    background:white; margin:0 auto 8px; position:relative; z-index:1; }
.tl-dot.done { background:#FFE835; }
.tl-dot.best { background:#FF4081; }
.tl-label { font-family:'Noto Sans KR', sans-serif; font-size:1rem; font-weight:700; color:#222; margin-bottom:2px; }
.tl-sub { font-family:'Noto Sans KR', sans-serif; font-size:.8rem; color:#888; line-height:1.3; }
.tl-badge { display:inline-block; font-family:'Noto Sans KR', sans-serif; font-size:.72rem; font-weight:700;
    padding:2px 8px; border:2px solid #222; border-radius:2px; margin-top:5px; }
.b-fail { background:#ffebee; color:#c62828; }
.b-ok   { background:#e8f5e9; color:#2e7d32; }
.b-best { background:#FF4081; color:white; }

.epoch-label { font-family:'Noto Sans KR', sans-serif; font-size:.95rem; font-weight:700; text-align:center; margin-top:4px; }
.epoch-badge { font-family:'Noto Sans KR', sans-serif; font-size:.75rem; text-align:center;
    margin-top:2px; padding:1px 5px; border-radius:3px; display:inline-block; width:100%; }

.info-box { font-family:'Noto Sans KR', sans-serif; font-size:.95rem; color:#666;
    margin-top:10px; padding:10px 14px; background:#fff9c4;
    border-left:3px solid #ffc107; border-radius:2px; line-height:1.6; }

.footer { text-align:center; font-family:'Noto Sans KR', sans-serif; font-size:.9rem;
    color:#c0bab0; margin-top:28px; line-height:1.9; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <div class="header-mascot">📊</div>
    <div>
        <h1>학습 리포트</h1>
        <div class="sub">SD v1.5 + LoRA 파인튜닝 · ControlNet 적용 과정</div>
    </div>
</div>
<div class="doodle-line">✏ ✦ 📈 ✦ ✏</div>
""", unsafe_allow_html=True)

nc1, nc2, nc3 = st.columns(3)
with nc1: st.page_link("app.py",                      label="✏️ 이모티콘 메이커", use_container_width=True)
with nc2: st.page_link("pages/01_학습_리포트.py",     label="📊 학습 리포트",     use_container_width=True)
with nc3: st.page_link("pages/02_그래프.py",          label="📈 성능 그래프",     use_container_width=True)
nr1, nr2, nr3 = st.columns(3)
with nr1: st.page_link("pages/03_EDA_데이터분석.py", label="🔍 데이터 분석",     use_container_width=True)
with nr2: st.page_link("pages/04_가중치분석.py",      label="⚖️ 가중치 분석",    use_container_width=True)
with nr3: st.page_link("pages/05_생성품질.py",        label="🖼️ 생성 품질",      use_container_width=True)

# ── 섹션 1: 모델 선택 이유 ───────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
<h2>🧠 모델 선택 이유</h2>
<table class="compare-table">
<tr>
  <th>비교 항목</th>
  <th>CNN (분류 · 검출)</th>
  <th>Diffusion + LoRA &nbsp;✅ 채택</th>
</tr>
<tr>
  <td><b>역할</b></td>
  <td class="bad">이미지 <b>분류 · 검출</b><br>(고양이=98% 등)</td>
  <td class="good">이미지 <b>생성</b><br>(없던 이모티콘을 새로 만들기)</td>
</tr>
<tr>
  <td><b>과제 적합성</b></td>
  <td class="bad">❌ 생성 기능 없음</td>
  <td class="good">✅ 손그림 → 이모티콘 변환 가능</td>
</tr>
<tr>
  <td><b>필요 데이터량</b></td>
  <td class="bad">수만 장 이상</td>
  <td class="good">230장으로 파인튜닝 가능 (LoRA)</td>
</tr>
<tr>
  <td><b>GPU 요구량</b></td>
  <td class="bad">전체 학습 = VRAM 24GB+</td>
  <td class="good">LoRA = Colab T4(16GB) 충분</td>
</tr>
<tr>
  <td><b>스케치 반영</b></td>
  <td class="bad">❌ 불가</td>
  <td class="good">✅ ControlNet으로 손그림 가이드</td>
</tr>
</table>

<div class="point-row">
  <div class="point-card">
    <div class="pt">🔧 LoRA 선택 이유</div>
    <div class="pv">전체 파인튜닝 대비<br><b>파라미터 0.1%만 학습</b><br>r=32 / alpha=16<br>표현력 ↔ 안정성 균형점</div>
  </div>
  <div class="point-card">
    <div class="pt">📐 ControlNet 추가 이유</div>
    <div class="pv">LoRA만으론 <b>랜덤 생성</b><br>ControlNet(scribble)이<br><b>손그림 선을 가이드</b>로 전달</div>
  </div>
  <div class="point-card">
    <div class="pt">⚙️ 옵티마이저</div>
    <div class="pv"><b>AdamW</b> · lr=1e-4<br>cosine_with_restarts<br>warmup 100 steps</div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 2: 실험 3단계 흐름 ──────────────────────────────────────────────────
st.markdown("""
<div class="section-card r2">
<h2>🗂️ 실험 3단계 흐름</h2>
<div class="timeline">
  <div class="tl-item">
    <div class="tl-line"></div>
    <div class="tl-dot done"></div>
    <div class="tl-label">실험 1</div>
    <div class="tl-sub">전체 Twemoji 3,689장<br>5 epoch · 1,464 steps</div>
    <div class="tl-badge b-fail">NSFW 필터 오류</div>
  </div>
  <div class="tl-item">
    <div class="tl-line"></div>
    <div class="tl-dot done"></div>
    <div class="tl-label">실험 2</div>
    <div class="tl-sub">동물 얼굴 46 → 230장<br>(증강) · 8 epoch</div>
    <div class="tl-badge b-ok">품질 대폭 개선</div>
  </div>
  <div class="tl-item">
    <div class="tl-line"></div>
    <div class="tl-dot best"></div>
    <div class="tl-label">실험 3</div>
    <div class="tl-sub">epoch_8 이어받아<br>epoch_9~10 추가 학습</div>
    <div class="tl-badge b-best">epoch_7 최종 채택 ✅</div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 3: 에폭별 이미지 비교 ───────────────────────────────────────────────
st.markdown('<div class="section-card"><h2>🖼️ 에폭별 생성 결과 비교</h2>', unsafe_allow_html=True)

epoch_info = [
    ("epoch_0_baseline.png", "Epoch 0",    "학습 전 기준선",    "#f0f0f0"),
    ("epoch_1.png",          "Epoch 1",    "❌ 얼굴 콜라주",    "#ffcdd2"),
    ("epoch_3.png",          "Epoch 3",    "흑백 타일 패턴",    "#fff9c4"),
    ("epoch_5.png",          "Epoch 5",    "단일화, 채색 없음", "#fff9c4"),
    ("epoch_7.png",          "Epoch 7 ✅", "✨ 최적 채택",      "#fce4ec"),
    ("epoch_9.png",          "Epoch 9",    "배경 색상 이상",    "#e8f5e9"),
    ("epoch_10.png",         "Epoch 10",   "❌ 과적합",         "#ffcdd2"),
]

cols = st.columns(4)
for i, (fname, label, badge, color) in enumerate(epoch_info):
    path = os.path.join(SAMPLES_DIR, fname)
    is_best = "✅" in label
    with cols[i % 4]:
        if os.path.exists(path):
            img = Image.open(path)
            st.image(img, use_container_width=True)
        label_color = "#FF4081" if is_best else "#222"
        st.markdown(
            f'<div class="epoch-label" style="color:{label_color};">{label}</div>'
            f'<div class="epoch-badge" style="background:{color};border:1.5px solid #ccc;">{badge}</div>',
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

# ── 섹션 4: Loss 그래프 ───────────────────────────────────────────────────────
st.markdown('<div class="section-card r2"><h2>📉 학습 Loss 곡선 (실험 2 · epoch 1~9)</h2>', unsafe_allow_html=True)

epochs   = list(range(1, 10))
avg_loss = [0.0446, 0.0385, 0.0416, 0.0430, 0.0454, 0.0383, 0.0427, 0.0430, 0.0420]

fig, ax = plt.subplots(figsize=(9, 3.8))
fig.patch.set_facecolor("#faf8f3")
ax.set_facecolor("#faf8f3")

ax.plot(epochs, avg_loss, color="#222", linewidth=2.5,
        marker="o", markersize=7, markerfacecolor="white", markeredgewidth=2.5, zorder=3)

# epoch 7 강조
ax.scatter([7], [avg_loss[6]], s=200, color="#FF4081", zorder=4)
ax.annotate("Epoch 7 채택 ✅",
            xy=(7, avg_loss[6]), xytext=(7.3, avg_loss[6] + 0.0025),
            fontsize=9, color="#FF4081", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#FF4081", lw=1.5))

ax.set_xlabel("Epoch", fontsize=11)
ax.set_ylabel("Avg Loss", fontsize=11)
ax.set_title("동물 얼굴 LoRA 학습 Loss", fontsize=13, pad=10)
ax.set_xticks(epochs)
ax.set_ylim(0.028, 0.062)
ax.grid(True, linestyle="--", alpha=0.35, color="#ccc")
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color("#222")

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.markdown("""
<div class="info-box">
💡 Loss 진동 원인: 배치 크기 1~4로 작아 스텝마다 분산이 큼.
epoch 6이 수치상 최솟값(0.0383)이지만, 시각 품질 기준으로 <b>epoch 7이 가장 Twemoji스러워</b> 최종 채택.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">✏️ ～ 📊 ～ 😸 · SD v1.5 + LoRA + ControlNet 학습 리포트</div>',
            unsafe_allow_html=True)
