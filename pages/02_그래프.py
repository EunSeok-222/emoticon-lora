import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="성능 그래프", page_icon="📈", layout="centered",
                   initial_sidebar_state="collapsed")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700;900&display=swap');
.stApp {
    background-color: #faf8f3;
    background-image: radial-gradient(circle, #ccc8bf 1px, transparent 1px);
    background-size: 20px 20px; font-family: 'Caveat', cursive;
}
.main .block-container { padding-top: 1.2rem; max-width: 820px; }

[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }

[data-testid="collapsedControl"] { display: none !important; }

a[data-testid="stPageLink-NavLink"] {
    font-family: 'Caveat', cursive !important;
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
.header-card h1 { font-family:'Caveat',cursive; font-size:2.3rem; font-weight:900; color:#222; margin:0 0 4px; }
.header-card .sub { font-family:'Caveat',cursive; font-size:1.1rem; color:#777; }
.doodle-line { text-align:center; font-size:1rem; color:#d0cbbf; letter-spacing:8px; margin:6px 0 14px; }
.section-card {
    background: white; border: 2.5px solid #222;
    border-radius: 5px 3px 6px 4px / 4px 6px 3px 5px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 5px 5px 0 #222;
}
.section-card.r2 { transform: rotate(-0.15deg); }
.section-card h2 { font-family:'Caveat',cursive; font-size:1.7rem; font-weight:900;
    color:#222; margin:0 0 14px; border-bottom:2px dashed #ccc; padding-bottom:8px; }
.info-box { font-family:'Caveat',cursive; font-size:.95rem; color:#555;
    margin-top:10px; padding:10px 14px; background:#fff9c4;
    border-left:3px solid #ffc107; border-radius:2px; line-height:1.6; }
.metric-row { display:flex; gap:10px; margin-top:6px; flex-wrap:wrap; }
.metric-card { flex:1; min-width:130px; text-align:center;
    background:white; border:2.5px solid #222;
    border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:12px 8px; box-shadow:3px 3px 0 #222; }
.metric-card .mv { font-family:'Caveat',cursive; font-size:1.8rem; font-weight:900; }
.metric-card .ml { font-family:'Caveat',cursive; font-size:.85rem; color:#777; margin-top:3px; }
.footer { text-align:center; font-family:'Caveat',cursive; font-size:.9rem;
    color:#c0bab0; margin-top:28px; line-height:1.9; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <div class="header-mascot">📈</div>
    <div>
        <h1>성능 그래프</h1>
        <div class="sub">실험별 Loss 비교 · 에폭별 수렴 분석</div>
    </div>
</div>
<div class="doodle-line">✏ ✦ 📉 ✦ ✏</div>
""", unsafe_allow_html=True)

nc1, nc2, nc3 = st.columns(3)
with nc1: st.page_link("app.py", label="✏️ 이모티콘 메이커", use_container_width=True)
with nc2: st.page_link("pages/01_학습_리포트.py", label="📊 학습 리포트", use_container_width=True)
with nc3: st.page_link("pages/02_그래프.py", label="📈 성능 그래프", use_container_width=True)

# ── 핵심 수치 요약 ────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
<h2>📌 실험 요약 수치</h2>
<div class="metric-row">
  <div class="metric-card">
    <div class="mv" style="color:#888;">3,689</div>
    <div class="ml">실험 1 데이터<br>(전체 Twemoji)</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#FF4081;">230</div>
    <div class="ml">실험 2 데이터<br>(동물 얼굴 증강)</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#222;">0.0383</div>
    <div class="ml">최저 Loss<br>(epoch 6)</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#FF4081;">7</div>
    <div class="ml">최종 채택 Epoch<br>(시각 품질 기준)</div>
  </div>
  <div class="metric-card">
    <div class="mv" style="color:#222;">0.1%</div>
    <div class="ml">LoRA 학습<br>파라미터 비율</div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

# ── 데이터 ────────────────────────────────────────────────────────────────────
# 실험 1: 전체 Twemoji, 5 epochs (step 샘플 기반 근사 avg)
exp1_epochs = [1, 2, 3, 4, 5]
exp1_loss   = [0.054, 0.020, 0.069, 0.044, 0.012]

# 실험 2+3: 동물 얼굴, epoch avg 실측값
exp2_epochs = list(range(1, 10))
exp2_loss   = [0.0446, 0.0385, 0.0416, 0.0430, 0.0454, 0.0383, 0.0427, 0.0430, 0.0420]

quality = {
    1: ("언더피팅",    "#ffcdd2"),
    2: ("개선 중",     "#fff9c4"),
    3: ("흑백 패턴",   "#fff9c4"),
    4: ("형태 안정",   "#fff9c4"),
    5: ("단일화",      "#e8f5e9"),
    6: ("Loss 최솟값", "#e8f5e9"),
    7: ("✅ 최적 채택","#fce4ec"),
    8: ("과적합 시작", "#fff9c4"),
    9: ("배경 이상",   "#fff9c4"),
}

# ── 그래프 1: 실험 1 vs 실험 2 비교 ──────────────────────────────────────────
st.markdown('<div class="section-card r2"><h2>📊 실험 1 vs 실험 2 Loss 비교</h2>',
            unsafe_allow_html=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
fig.patch.set_facecolor("#faf8f3")

# 실험 1
ax1.set_facecolor("#faf8f3")
ax1.plot(exp1_epochs, exp1_loss, color="#888", linewidth=2.5,
         marker="o", markersize=7, markerfacecolor="white", markeredgewidth=2.5)
ax1.fill_between(exp1_epochs, exp1_loss, alpha=0.08, color="#888")
ax1.set_title("실험 1 — 전체 Twemoji\n(3,689장 · 5 epoch)", fontsize=10, pad=8)
ax1.set_xlabel("Epoch"); ax1.set_ylabel("Avg Loss (근사)")
ax1.set_xticks(exp1_epochs); ax1.set_ylim(0, 0.10)
ax1.grid(True, linestyle="--", alpha=0.3, color="#ccc")
ax1.text(3.0, 0.078, "NSFW 필터 오류\n→ 실험 중단", fontsize=8.5,
         color="#c62828", ha="center",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffebee",
                   edgecolor="#c62828", linewidth=1.5))
for sp in ax1.spines.values():
    sp.set_linewidth(1.5); sp.set_color("#222")

# 실험 2+3
ax2.set_facecolor("#faf8f3")
ax2.plot(exp2_epochs, exp2_loss, color="#222", linewidth=2.5,
         marker="o", markersize=7, markerfacecolor="white",
         markeredgewidth=2.5, zorder=3)
ax2.fill_between(exp2_epochs, exp2_loss, alpha=0.06, color="#222")
ax2.scatter([7], [exp2_loss[6]], s=200, color="#FF4081", zorder=4)
ax2.axvline(x=7, color="#FF4081", linestyle="--", linewidth=1.2, alpha=0.5)
ax2.annotate("Epoch 7\n채택 ✅", xy=(7, exp2_loss[6]),
             xytext=(7.5, exp2_loss[6] + 0.003),
             fontsize=8.5, color="#FF4081", fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#FF4081", lw=1.2))
ax2.set_title("실험 2+3 — 동물 얼굴\n(230장 증강 · 9 epoch)", fontsize=10, pad=8)
ax2.set_xlabel("Epoch"); ax2.set_ylabel("Avg Loss")
ax2.set_xticks(exp2_epochs); ax2.set_ylim(0.028, 0.062)
ax2.grid(True, linestyle="--", alpha=0.3, color="#ccc")
for sp in ax2.spines.values():
    sp.set_linewidth(1.5); sp.set_color("#222")

plt.tight_layout(pad=2.0)
st.pyplot(fig)
plt.close(fig)

st.markdown("""
<div class="info-box">
💡 실험 1은 NSFW 필터 오류로 결과물이 검은 이미지로 출력됨 →
데이터를 동물 얼굴(46종)로 좁히고 증강(230장)하여 실험 2 진행.
실험 2의 Loss(avg ~0.04)가 더 안정적으로 수렴함.
</div>
</div>
""", unsafe_allow_html=True)

# ── 그래프 2: 에폭별 상세 Loss 바 차트 ───────────────────────────────────────
st.markdown('<div class="section-card"><h2>🔍 에폭별 상세 Loss & 품질 평가</h2>',
            unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(10, 4.2))
fig.patch.set_facecolor("#faf8f3")
ax.set_facecolor("#faf8f3")

bar_colors = [
    "#FF4081" if e == 7 else "#555" if e == 6 else "#bbb"
    for e in exp2_epochs
]
bars = ax.bar(exp2_epochs, exp2_loss, color=bar_colors,
              width=0.55, edgecolor="#222", linewidth=1.5, zorder=2)
ax.plot(exp2_epochs, exp2_loss, color="#222", linewidth=1.8,
        marker="o", markersize=5, markerfacecolor="white",
        markeredgewidth=1.8, zorder=3, linestyle="--", alpha=0.5)

for bar, val in zip(bars, exp2_loss):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.0003,
            f"{val:.4f}", ha="center", va="bottom", fontsize=8, color="#222")

ax.set_xlabel("Epoch", fontsize=11)
ax.set_ylabel("Avg Loss", fontsize=11)
ax.set_title("에폭별 평균 Loss (실험 2+3)", fontsize=13, pad=10)
ax.set_xticks(exp2_epochs)
ax.set_ylim(0.030, 0.058)
ax.grid(True, axis="y", linestyle="--", alpha=0.3, color="#ccc")

p1 = mpatches.Patch(color="#FF4081", label="Epoch 7 — 최종 채택")
p2 = mpatches.Patch(color="#555",   label="Epoch 6 — Loss 최솟값")
p3 = mpatches.Patch(color="#bbb",   label="기타 epoch")
ax.legend(handles=[p1, p2, p3], fontsize=9, loc="upper right",
          framealpha=0.9, edgecolor="#222")
for sp in ax.spines.values():
    sp.set_linewidth(1.5); sp.set_color("#222")

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# 품질 평가 테이블
rows_html = "".join([
    f'<tr>'
    f'<td style="font-family:Caveat,cursive;padding:7px 14px;border:1.5px solid #ddd;'
    f'{"font-weight:700;color:#FF4081;" if e==7 else ""}">Epoch {e}</td>'
    f'<td style="font-family:Caveat,cursive;padding:7px 14px;border:1.5px solid #ddd;">'
    f'{"<b>" if e in (6,7) else ""}{exp2_loss[e-1]:.4f}{"</b>" if e in (6,7) else ""}</td>'
    f'<td style="font-family:Caveat,cursive;padding:7px 14px;border:1.5px solid #ddd;background:{c};">{q}</td>'
    f'</tr>'
    for e, (q, c) in quality.items()
])
st.markdown(f"""
<br>
<table style="width:100%;border-collapse:collapse;font-size:1rem;">
<tr>
  <th style="font-family:Caveat,cursive;background:#222;color:white;padding:8px 14px;border:2px solid #222;text-align:left;">Epoch</th>
  <th style="font-family:Caveat,cursive;background:#222;color:white;padding:8px 14px;border:2px solid #222;text-align:left;">Avg Loss</th>
  <th style="font-family:Caveat,cursive;background:#222;color:white;padding:8px 14px;border:2px solid #222;text-align:left;">시각 품질 평가</th>
</tr>
{rows_html}
</table>
<div class="info-box" style="margin-top:12px;">
📌 Loss 수치와 시각 품질이 항상 일치하지 않음.
epoch 6이 수치상 최저(0.0383)이지만 이미지가 흐릿함.
<b>epoch 7</b>이 단일 얼굴 + 컬러 + Twemoji 스타일 셋 다 만족 → 최종 채택.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">✏️ ～ 📈 ～ 😸 · 실험 성능 비교 그래프</div>',
            unsafe_allow_html=True)
