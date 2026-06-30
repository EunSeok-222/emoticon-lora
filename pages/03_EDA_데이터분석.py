import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams.update({'font.family': 'AppleGothic', 'axes.unicode_minus': False})
import numpy as np

st.set_page_config(page_title="데이터 분석", page_icon="🔍", layout="centered",
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
.flow-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap;
    justify-content:center; margin:10px 0; }
.flow-box { text-align:center; background:white; border:2.5px solid #222;
    border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:10px 16px; box-shadow:3px 3px 0 #222; min-width:100px; }
.flow-box .fnum { font-family:'Noto Sans KR', sans-serif; font-size:2rem; font-weight:900; }
.flow-box .flbl { font-family:'Noto Sans KR', sans-serif; font-size:.82rem; color:#777; }
.flow-arrow { font-family:'Noto Sans KR', sans-serif; font-size:1.6rem; color:#aaa; font-weight:900; }
.flow-box.highlight { background:#FFE835; }
.flow-box.best { background:#FF4081; }
.flow-box.best .flbl { color:rgba(255,255,255,.8); }
.aug-row { display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
.aug-card { flex:1; min-width:120px; background:#fffde7;
    border:2px solid #222; border-radius:3px 5px 4px 3px / 4px 3px 5px 4px;
    padding:10px 12px; box-shadow:3px 3px 0 #222; }
.aug-card .at { font-family:'Noto Sans KR', sans-serif; font-size:.78rem; font-weight:700;
    letter-spacing:1px; color:#999; margin-bottom:4px; text-transform:uppercase; }
.aug-card .av { font-family:'Noto Sans KR', sans-serif; font-size:.9rem; color:#222; line-height:1.4; }
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
    <div class="header-mascot">🔍</div>
    <div>
        <h1>EDA 데이터 분석</h1>
        <div class="sub">학습 데이터 수집 · 필터링 · 증강 과정</div>
    </div>
</div>
<div class="doodle-line">✏ ✦ 📊 ✦ ✏</div>
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

# ── 섹션 1: 데이터 수집 흐름 ─────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
<h2>📦 데이터 수집 → 학습까지 흐름</h2>
<div class="flow-row">
  <div class="flow-box">
    <div class="fnum" style="color:#888;">3,689</div>
    <div class="flbl">Twemoji v14<br>전체 PNG 72×72</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-box highlight">
    <div class="fnum" style="color:#222;">~194</div>
    <div class="flbl">유니코드<br>필터링 후</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">
    <div class="fnum" style="color:#555;">46</div>
    <div class="flbl">동물 얼굴<br>수동 선별</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-box best">
    <div class="fnum" style="color:white;">230</div>
    <div class="flbl">증강 후<br>최종 학습 데이터</div>
  </div>
</div>
<div class="info-box">
💡 처음엔 전체 3,689장(실험 1)으로 학습했지만 NSFW 필터 오류로 실패.
유니코드 범위로 얼굴·동물·사람 이모지만 추려 동물 얼굴 46장 선별 → 5배 증강으로 230장 확보(실험 2+3).
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 2: 필터링 전후 비교 바차트 ─────────────────────────────────────────
st.markdown('<div class="section-card r2"><h2>✂️ 단계별 데이터 수 비교</h2>', unsafe_allow_html=True)

stages = ["전체\nTwemoji", "유니코드\n필터링 후", "동물 얼굴\n선별", "증강 후\n(최종)"]
counts = [3689, 194, 46, 230]
colors = ["#ccc", "#FFE835", "#aaa", "#FF4081"]

fig, ax = plt.subplots(figsize=(9, 4))
fig.patch.set_facecolor("#faf8f3"); ax.set_facecolor("#faf8f3")
bars = ax.bar(stages, counts, color=colors, edgecolor="#222", linewidth=2, width=0.5)
for bar, val in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 40,
            f"{val:,}", ha="center", va="bottom", fontsize=12, fontweight="bold", color="#222")
ax.set_ylabel("이미지 수", fontsize=11)
ax.set_title("단계별 데이터 수 변화", fontsize=13, pad=10)
ax.set_ylim(0, 4400)
ax.grid(True, axis="y", linestyle="--", alpha=0.3, color="#ccc")
for sp in ax.spines.values(): sp.set_linewidth(1.5); sp.set_color("#222")
ax.tick_params(axis="x", labelsize=10)
plt.tight_layout()
st.pyplot(fig); plt.close(fig)
st.markdown("</div>", unsafe_allow_html=True)

# ── 섹션 3: 카테고리별 유니코드 분포 ────────────────────────────────────────
st.markdown('<div class="section-card"><h2>🗂️ 필터링 기준 — 카테고리별 분포</h2>', unsafe_allow_html=True)

categories  = ["얼굴 표정\n(😀~🙏)", "동물\n(🐀~🐿)", "사람\n(👦~💇)", "사람 판타지\n(🧐~🧟)"]
cat_counts  = [80, 64, 34, 16]
cat_colors  = ["#FF4081", "#FFE835", "#888", "#ccc"]
unicode_ranges = ["0x1F600–0x1F64F", "0x1F400–0x1F43F", "0x1F466–0x1F487", "0x1F9D0–0x1F9DF"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
fig.patch.set_facecolor("#faf8f3")

ax1.set_facecolor("#faf8f3")
_, _, autotexts = ax1.pie(
    cat_counts, labels=categories, colors=cat_colors,
    autopct="%1.0f%%", startangle=140,
    wedgeprops=dict(edgecolor="#222", linewidth=2),
    textprops=dict(fontsize=9),
)
for at in autotexts: at.set_fontsize(9); at.set_fontweight("bold")
ax1.set_title("카테고리별 비율 (~194장)", fontsize=11, pad=10)

ax2.set_facecolor("#faf8f3")
bars2 = ax2.barh(range(len(categories)), cat_counts, color=cat_colors,
                 edgecolor="#222", linewidth=1.8, height=0.55)
for bar, val, ur in zip(bars2, cat_counts, unicode_ranges):
    ax2.text(val + 1, bar.get_y() + bar.get_height() / 2,
             f"{val}장  {ur}", va="center", fontsize=8.5, color="#555")
ax2.set_yticks(range(len(categories))); ax2.set_yticklabels(categories, fontsize=9)
ax2.set_xlabel("이미지 수", fontsize=10); ax2.set_xlim(0, 125)
ax2.set_title("카테고리별 이미지 수", fontsize=11, pad=10)
ax2.grid(True, axis="x", linestyle="--", alpha=0.3, color="#ccc")
for sp in ax2.spines.values(): sp.set_linewidth(1.5); sp.set_color("#222")
plt.tight_layout()
st.pyplot(fig); plt.close(fig)

st.markdown("""
<div class="info-box">
📌 3,689장 중 얼굴·동물·사람 4개 유니코드 범위(~194장)만 유지.
손·물건·기호 이모지는 학습 품질 저하 원인으로 제거.
이후 동물 얼굴 46장을 수동 선별.
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 4: 데이터 증강 방법 ─────────────────────────────────────────────────
st.markdown("""
<div class="section-card r2">
<h2>🔄 데이터 증강 — 46장 → 230장 (5×)</h2>
<div class="aug-row">
  <div class="aug-card"><div class="at">① 원본</div>
    <div class="av">원본 PNG 그대로<br>흰 배경 · 72×72</div></div>
  <div class="aug-card"><div class="at">② 채도 강화</div>
    <div class="av">ImageEnhance<br>Color × 1.4<br>선명하게</div></div>
  <div class="aug-card"><div class="at">③ 밝기 조정</div>
    <div class="av">ImageEnhance<br>Brightness × 1.15<br>약간 밝게</div></div>
  <div class="aug-card"><div class="at">④ 중앙 크롭</div>
    <div class="av">얼굴 중심<br>50×50 크롭<br>→ 72×72 리사이즈</div></div>
  <div class="aug-card"><div class="at">⑤ 대비 강화</div>
    <div class="av">ImageEnhance<br>Contrast × 1.2<br>윤곽 또렷하게</div></div>
</div>
<div class="info-box" style="margin-top:12px;">
💡 수평 플립은 이모티콘의 비대칭 표정 왜곡 우려로 제외.
5종 증강 × 46장 = 230장으로 LoRA 학습에 충분한 다양성 확보.
</div>
</div>
""", unsafe_allow_html=True)

# ── 섹션 5: LoRA 학습 설정 ───────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
<h2>⚙️ LoRA 파인튜닝 하이퍼파라미터</h2>
<table style="width:100%;border-collapse:collapse;font-family:'Noto Sans KR', sans-serif;font-size:1rem;">
<tr>
  <th style="background:#222;color:white;padding:8px 14px;border:2px solid #222;text-align:left;">항목</th>
  <th style="background:#222;color:white;padding:8px 14px;border:2px solid #222;text-align:left;">실험 1 (전체 Twemoji)</th>
  <th style="background:#222;color:white;padding:8px 14px;border:2px solid #222;text-align:left;">실험 2+3 (동물 얼굴)</th>
</tr>
<tr><td style="padding:8px 14px;border:1.5px solid #ddd;">베이스 모델</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">SD v1.5 (runwayml/stable-diffusion-v1-5)</td></tr>
<tr style="background:#f9f7f2;"><td style="padding:8px 14px;border:1.5px solid #ddd;">학습 데이터</td>
    <td style="padding:8px 14px;border:1.5px solid #ddd;">3,689장</td>
    <td style="padding:8px 14px;border:1.5px solid #ddd;font-weight:700;color:#FF4081;">230장 (46 × 5배 증강)</td></tr>
<tr><td style="padding:8px 14px;border:1.5px solid #ddd;">LoRA rank (r)</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">32</td></tr>
<tr style="background:#f9f7f2;"><td style="padding:8px 14px;border:1.5px solid #ddd;">LoRA alpha (α)</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">16 → 스케일 = α/r = 0.5</td></tr>
<tr><td style="padding:8px 14px;border:1.5px solid #ddd;">적용 레이어</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">to_q · to_k · to_v · to_out.0 (UNet Cross-Attention)</td></tr>
<tr style="background:#f9f7f2;"><td style="padding:8px 14px;border:1.5px solid #ddd;">Learning Rate</td>
    <td style="padding:8px 14px;border:1.5px solid #ddd;">1e-5</td>
    <td style="padding:8px 14px;border:1.5px solid #ddd;">1e-5 → 5e-6 (epoch 9 이어받기 시)</td></tr>
<tr><td style="padding:8px 14px;border:1.5px solid #ddd;">옵티마이저</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">AdamW</td></tr>
<tr style="background:#f9f7f2;"><td style="padding:8px 14px;border:1.5px solid #ddd;">배치 크기</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">1</td></tr>
<tr><td style="padding:8px 14px;border:1.5px solid #ddd;">에포크</td>
    <td style="padding:8px 14px;border:1.5px solid #ddd;">5 (NSFW 오류로 중단)</td>
    <td style="padding:8px 14px;border:1.5px solid #ddd;font-weight:700;">8 epoch + 추가 2 epoch = 총 10 epoch</td></tr>
<tr style="background:#f9f7f2;"><td style="padding:8px 14px;border:1.5px solid #ddd;">동결 레이어</td>
    <td colspan="2" style="padding:8px 14px;border:1.5px solid #ddd;">VAE · Text Encoder (전체 고정)</td></tr>
</table>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">✏️ ～ 🔍 ～ 😸 · EDA 데이터 분석 · SD v1.5 + LoRA</div>',
            unsafe_allow_html=True)
