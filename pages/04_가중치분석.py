import os
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib
matplotlib.rcParams.update({'font.family': 'AppleGothic', 'axes.unicode_minus': False})
import numpy as np

st.set_page_config(page_title="가중치 분석", page_icon="⚖️", layout="centered",
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
.main .block-container { padding-top: 1.2rem; max-width: 820px; }
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
.metric-row { display:flex; gap:10px; margin:10px 0; flex-wrap:wrap; }
.metric-card { flex:1; min-width:130px; text-align:center; background:white;
    border:2.5px solid #222; border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:12px 8px; box-shadow:3px 3px 0 #222; }
.metric-card .mv { font-family:'Noto Sans KR', sans-serif; font-size:1.7rem; font-weight:900; }
.metric-card .ml { font-family:'Noto Sans KR', sans-serif; font-size:.8rem; color:#777; margin-top:2px; }
.layer-row { display:flex; gap:8px; flex-wrap:wrap; margin:10px 0; }
.layer-tag { font-family:'Noto Sans KR', sans-serif; font-size:.95rem; font-weight:700;
    padding:4px 12px; border:2px solid #222; border-radius:3px; }
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
    <div class="header-mascot">⚖️</div>
    <div>
        <h1>LoRA 가중치 분석</h1>
        <div class="sub">파라미터 비교 · 레이어별 가중치 분포 (epoch_7)</div>
    </div>
</div>
<div class="doodle-line">✏ ✦ 📐 ✦ ✏</div>
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

# ── 가중치 로드 ───────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LORA_PATH = os.path.join(BASE_DIR, "lora_animal", "epoch_7", "adapter_model.safetensors")

@st.cache_data
def load_weights(path):
    from safetensors.torch import load_file
    return {k: v.float().numpy() for k, v in load_file(path).items()}

weights = load_weights(LORA_PATH)
lt_labels = ["to_q", "to_k", "to_v", "to_out"]
lt_colors = ["#FF4081", "#FFE835", "#888", "#ccc"]

layer_types = {lt: [] for lt in lt_labels}
for k, v in weights.items():
    for lt in lt_labels:
        if lt in k:
            layer_types[lt].append(v.flatten())
            break

flat = {lt: np.concatenate(arrs) for lt, arrs in layer_types.items()}
total_params = sum(v.size for v in weights.values())

# ── 섹션 1: 파라미터 수 비교 ─────────────────────────────────────────────────
st.markdown(f"""
<div class="section-card">
<h2>📊 파라미터 수 비교 — SD UNet vs LoRA</h2>
<div class="metric-row">
  <div class="metric-card">
    <div class="mv" style="color:#ccc;">860M</div>
    <div class="ml">SD v1.5 UNet<br>전체 파라미터</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#FF4081;">{total_params/1e6:.1f}M</div>
    <div class="ml">LoRA epoch_7<br>학습된 파라미터</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#222;">{total_params/860e6*100:.2f}%</div>
    <div class="ml">전체 대비<br>LoRA 비율</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#555;">256</div>
    <div class="ml">LoRA 텐서 수<br>(4 레이어 × 64)</div>
  </div>
</div>
<div class="layer-row">
  <span class="layer-tag" style="background:#FF4081;color:white;">to_q × 64</span>
  <span class="layer-tag" style="background:#FFE835;color:#222;">to_k × 64</span>
  <span class="layer-tag" style="background:#888;color:white;">to_v × 64</span>
  <span class="layer-tag" style="background:#f0f0f0;color:#222;border-color:#aaa;">to_out × 64</span>
</div>
<div class="info-box">
📌 LoRA는 각 Attention 레이어에 저랭크 행렬 A[32×320] + B[320×32] 두 개를 추가.
ΔW = (α/r) × B×A 로 원본 가중치를 수정. 전체 UNet 860M 중 {total_params/1e6:.1f}M ({total_params/860e6*100:.2f}%)만 학습.
VAE · Text Encoder는 완전 동결.
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 2: 레이어별 파라미터 수 ─────────────────────────────────────────────
st.markdown('<div class="section-card r2"><h2>📐 레이어별 파라미터 수</h2>', unsafe_allow_html=True)

lt_params = [sum(v.size for v in layer_types[lt]) for lt in lt_labels]
fig, ax = plt.subplots(figsize=(8, 3.5))
fig.patch.set_facecolor("#faf8f3"); ax.set_facecolor("#faf8f3")
bars = ax.barh(lt_labels, lt_params, color=lt_colors, edgecolor="#222", linewidth=1.8, height=0.5)
for bar, val in zip(bars, lt_params):
    ax.text(val + 1500, bar.get_y() + bar.get_height() / 2,
            f"{val/1e6:.2f}M", va="center", fontsize=10, color="#222")
ax.set_xlabel("파라미터 수", fontsize=11)
ax.set_title("레이어 타입별 LoRA 파라미터 수 (epoch_7)", fontsize=12, pad=10)
ax.grid(True, axis="x", linestyle="--", alpha=0.3, color="#ccc")
for sp in ax.spines.values(): sp.set_linewidth(1.5); sp.set_color("#222")
plt.tight_layout()
st.pyplot(fig); plt.close(fig)
st.markdown("</div>", unsafe_allow_html=True)

# ── 섹션 3: 가중치 히스토그램 ───────────────────────────────────────────────
st.markdown('<div class="section-card"><h2>📉 레이어별 가중치 분포 히스토그램</h2>', unsafe_allow_html=True)

fig = plt.figure(figsize=(11, 7.5))
fig.patch.set_facecolor("#faf8f3")
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.5, wspace=0.35)

for idx, (lt, color) in enumerate(zip(lt_labels, lt_colors)):
    ax = fig.add_subplot(gs[idx // 2, idx % 2])
    ax.set_facecolor("#faf8f3")
    data = flat[lt]
    ec = "#ccc" if color in ("#ccc", "#FFE835") else "none"
    ax.hist(data, bins=80, color=color, edgecolor=ec, alpha=0.85)
    ax.axvline(data.mean(), color="#222", linestyle="--", linewidth=1.5,
               label=f"mean={data.mean():.5f}")
    ax.axvline(0, color="#999", linestyle=":", linewidth=1)
    ax.set_title(f"{lt}  std={data.std():.4f}", fontsize=11, pad=6)
    ax.set_xlabel("가중치 값", fontsize=9)
    ax.set_ylabel("빈도", fontsize=9)
    ax.legend(fontsize=8, framealpha=0.8)
    for sp in ax.spines.values(): sp.set_linewidth(1.2); sp.set_color("#222")

st.pyplot(fig); plt.close(fig)

std_vals = {lt: flat[lt].std() for lt in lt_labels}
max_lt = max(std_vals, key=std_vals.get)
st.markdown(f"""
<div class="info-box">
💡 모든 레이어에서 가중치가 0 근방에 정규분포 (mean ≈ 0).
{max_lt} 레이어의 std(={std_vals[max_lt]:.4f})가 가장 커서
출력 방향 변환에 가장 많이 기여한 것으로 추정.
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 4: lora_A vs lora_B L2 Norm ────────────────────────────────────────
st.markdown('<div class="section-card r2"><h2>🔬 lora_A vs lora_B 행렬 크기 비교</h2>', unsafe_allow_html=True)

a_norms, b_norms = [], []
for k, v in weights.items():
    if "lora_A" in k:
        b_key = k.replace("lora_A", "lora_B")
        if b_key in weights:
            a_norms.append(float(np.linalg.norm(v)))
            b_norms.append(float(np.linalg.norm(weights[b_key])))

x = np.arange(len(a_norms))
fig, ax = plt.subplots(figsize=(11, 3.8))
fig.patch.set_facecolor("#faf8f3"); ax.set_facecolor("#faf8f3")
ax.plot(x, a_norms, color="#FF4081", linewidth=1.5, label="lora_A [32×320]  (rank-down)", alpha=0.85)
ax.plot(x, b_norms, color="#222",    linewidth=1.5, label="lora_B [320×32]  (rank-up)",   alpha=0.85)
ax.fill_between(x, a_norms, alpha=0.08, color="#FF4081")
ax.fill_between(x, b_norms, alpha=0.06, color="#222")
ax.set_xlabel("레이어 인덱스 (to_q → to_k → to_v → to_out 순)", fontsize=10)
ax.set_ylabel("L2 Norm", fontsize=10)
ax.set_title("lora_A vs lora_B 행렬 L2 Norm (전 레이어, epoch_7)", fontsize=12, pad=10)
ax.legend(fontsize=10, framealpha=0.9, edgecolor="#222")
ax.grid(True, linestyle="--", alpha=0.3, color="#ccc")
for sp in ax.spines.values(): sp.set_linewidth(1.5); sp.set_color("#222")
plt.tight_layout()
st.pyplot(fig); plt.close(fig)

mean_a, mean_b = np.mean(a_norms), np.mean(b_norms)
st.markdown(f"""
<div class="info-box">
📌 lora_B 평균 L2 Norm={mean_b:.3f} > lora_A 평균 L2 Norm={mean_a:.3f}.
LoRA 초기화 시 lora_A=랜덤 가우시안, lora_B=0 으로 시작.
학습 후 lora_B 크기가 실제 가중치 업데이트 양을 더 직접적으로 반영함.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">✏️ ～ ⚖️ ～ 😸 · LoRA 가중치 분석 · epoch_7 adapter</div>',
            unsafe_allow_html=True)
