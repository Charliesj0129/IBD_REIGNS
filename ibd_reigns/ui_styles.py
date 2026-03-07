MOBILE_CSS = """
<style>

:root {
  --color-primary: #E8D5B7;
  --color-accent: #D4A574;
  --color-success: #81C784;
  --color-danger: #E57373;
  --color-warning: #FFB74D;
  --color-info: #64B5F6;
  --color-bg: #1A1A2E;
  --color-bg-deep: #12121F;
  --color-card-bg: #16213E;
  --color-card-bg-hover: #1F2F52;
  --color-text: #E8D5B7;
  --color-muted: #8A7A6A;
  --color-border: rgba(232,213,183,0.08);
  --shadow-sm: 0 4px 12px rgba(0,0,0,0.3);
  --shadow-md: 0 10px 30px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 20px rgba(212,165,116,0.15);
  --radius-lg: 20px;
  --radius-md: 12px;
}

/* ============================================
   GLOBAL RESET — Make Streamlit feel like a game
   ============================================ */
body, .stApp {
  font-family: 'Inter', system-ui, sans-serif;
  background-color: var(--color-bg) !important;
  color: var(--color-text);
}

h1, h2, h3, .gutreigns-title {
  font-family: 'Noto Serif TC', serif;
  font-weight: 700;
}

/* Hide ALL Streamlit chrome */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
.stDeployButton {display: none !important;}
.stDecoration {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
.block-container {padding-top: 0.8rem !important; padding-bottom: 1rem !important;}

/* ============================================
   SIDEBAR — Dark medieval profile panel
   ============================================ */
[data-testid="stSidebar"] {
  background: var(--color-bg-deep) !important;
  border-right: 1px solid var(--color-border) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"],
[data-testid="stSidebar"] .stMetric,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
  color: var(--color-text) !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
  color: var(--color-accent) !important;
  font-family: 'Noto Serif TC', serif !important;
}
[data-testid="stSidebar"] [data-testid="stMetricDelta"] {
  font-size: 0.75rem !important;
}
[data-testid="stSidebar"] hr {
  border-color: var(--color-border) !important;
}

/* ============================================
   BUTTONS — Glowing interactive game elements
   ============================================ */
.stButton > button {
  background: var(--color-card-bg) !important;
  color: var(--color-text) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Noto Serif TC', serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.03em !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  min-height: 44px !important;
}
.stButton > button:hover {
  background: var(--color-card-bg-hover) !important;
  border-color: var(--color-accent) !important;
  box-shadow: 0 0 16px rgba(212,165,116,0.2), var(--shadow-sm) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
  box-shadow: 0 0 8px rgba(212,165,116,0.15) !important;
}
/* Primary CTA button */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--color-accent), #C4956A) !important;
  color: var(--color-bg) !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 16px rgba(212,165,116,0.3) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
  box-shadow: 0 6px 24px rgba(212,165,116,0.45), 0 0 0 2px rgba(212,165,116,0.2) !important;
  transform: translateY(-2px) !important;
}

/* ============================================
   EXPANDERS — Sleek collapsible panels
   ============================================ */
[data-testid="stExpander"] {
  background: rgba(22, 33, 62, 0.5) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden;
}
[data-testid="stExpander"] summary {
  color: var(--color-muted) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  padding: 0.6rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
  color: var(--color-text) !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  border-top: 1px solid var(--color-border) !important;
}

/* ============================================
   PAGE FADE-IN — Smooth entry animation
   ============================================ */
@keyframes pageEnter {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.main .block-container {
  animation: pageEnter 0.35s ease-out;
}

/* ============================================
   TITLE & ORNAMENT
   ============================================ */
.gutreigns-title {
  font-size: 1.6rem;
  color: var(--color-primary);
  text-align: center;
  margin-bottom: 0.4rem;
  letter-spacing: 0.08em;
  text-shadow: 0 2px 12px rgba(232,213,183,0.12);
}

.gutreigns-ornament {
  width: 50px;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
  margin: 0 auto 1.2rem auto;
  border-radius: 2px;
}

/* ============================================
   STAT ICONS (REIGNS-STYLE 4-PILLAR)
   ============================================ */
.gutreigns-stat-row {
  display: flex;
  justify-content: center;
  gap: 1.8rem;
  margin: 0.6rem 0 1rem 0;
}
.gutreigns-stat-pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  position: relative;
}
.gutreigns-stat-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  border: 2px solid rgba(255,255,255,0.06);
  transition: all 0.3s ease;
}

.gutreigns-stat-fill {
  width: 6px;
  height: 40px;
  border-radius: 3px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
  position: relative;
}
.gutreigns-stat-fill-inner {
  position: absolute;
  bottom: 0;
  width: 100%;
  border-radius: 3px;
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s;
}
.pillar-health .gutreigns-stat-fill-inner { background: var(--color-danger); }
.pillar-immune .gutreigns-stat-fill-inner { background: var(--color-info); }
.pillar-sanity .gutreigns-stat-fill-inner { background: var(--color-success); }
.pillar-money .gutreigns-stat-fill-inner { background: var(--color-warning); }

/* Critical pulse */
.pillar-critical .gutreigns-stat-icon {
  animation: critPulse 1.2s infinite;
  border-color: var(--color-danger);
}
@keyframes critPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(229,115,115,0.3); }
  50% { box-shadow: 0 0 16px 4px rgba(229,115,115,0.5); }
}

/* Swipe preview highlight */
.pillar-preview-up .gutreigns-stat-icon {
  border-color: var(--color-success);
  box-shadow: 0 0 10px rgba(129,199,132,0.5);
  transform: scale(1.15);
}
.pillar-preview-down .gutreigns-stat-icon {
  border-color: var(--color-danger);
  box-shadow: 0 0 10px rgba(229,115,115,0.5);
  transform: scale(1.15);
}

/* ============================================
   STATUS BADGES
   ============================================ */
.gutreigns-status-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-bottom: 0.6rem;
}
.gutreigns-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  backdrop-filter: blur(4px);
}
.gutreigns-badge.flare {
  background: rgba(229,115,115,0.12);
  color: #E57373;
  border: 1px solid rgba(229,115,115,0.25);
  animation: critPulse 2s infinite;
}
.gutreigns-badge.moon-face {
  background: rgba(255,183,77,0.1);
  color: #FFB74D;
  border: 1px solid rgba(255,183,77,0.2);
}
.gutreigns-badge.sleep-deprived {
  background: rgba(186,104,200,0.1);
  color: #BA68C8;
  border: 1px solid rgba(186,104,200,0.2);
}
.gutreigns-badge.anemia {
  background: rgba(229,115,115,0.1);
  color: #E57373;
  border: 1px solid rgba(229,115,115,0.15);
}
.gutreigns-badge.remission {
  background: rgba(129,199,132,0.1);
  color: #81C784;
  border: 1px solid rgba(129,199,132,0.2);
}
.gutreigns-badge.steroid-dep {
  background: rgba(255,152,0,0.1);
  color: #FF9800;
  border: 1px solid rgba(255,152,0,0.15);
}
.gutreigns-badge.post-surgery {
  background: rgba(144,164,174,0.1);
  color: #90A4AE;
  border: 1px solid rgba(144,164,174,0.15);
}

/* ============================================
   WEEK / SEASON PROGRESS
   ============================================ */
.gutreigns-progress-wrap {
  margin: 0 0 0.8rem 0;
}
.gutreigns-progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--color-muted);
  margin-bottom: 3px;
  font-weight: 600;
}
.gutreigns-progress-bar {
  height: 4px;
  background: rgba(255,255,255,0.04);
  border-radius: 2px;
  overflow: hidden;
}
.gutreigns-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(90deg, var(--color-accent), var(--color-info));
}

/* ============================================
   EDUCATION INFO CARD
   ============================================ */
.gutreigns-edu {
  border-left: 3px solid var(--color-info);
  background: rgba(100,181,246,0.05);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: 0.7rem 0.9rem;
  margin: 0.6rem 0;
  animation: slideUp 0.3s ease-out;
}
.gutreigns-edu-title {
  font-family: 'Noto Serif TC', serif;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--color-info);
  margin-bottom: 0.25rem;
}
.gutreigns-edu-content {
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--color-text);
}
.gutreigns-edu-source {
  font-size: 0.68rem;
  color: var(--color-muted);
  margin-top: 0.25rem;
  font-style: italic;
}

/* ============================================
   ENDING SCREEN
   ============================================ */
.gutreigns-ending {
  text-align: center;
  padding: 2rem 1.5rem;
  border-radius: var(--radius-lg);
  margin: 1rem 0;
  animation: fadeIn 0.6s ease-out;
}
.gutreigns-ending.good {
  background: radial-gradient(ellipse at top, rgba(129,199,132,0.08) 0%, var(--color-bg) 70%);
  border: 1px solid rgba(129,199,132,0.12);
}
.gutreigns-ending.bad {
  background: radial-gradient(ellipse at top, rgba(229,115,115,0.08) 0%, var(--color-bg) 70%);
  border: 1px solid rgba(229,115,115,0.12);
}
.gutreigns-ending-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--color-primary);
}
.gutreigns-ending-desc {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--color-text);
  max-width: 480px;
  margin: 0 auto 1rem auto;
}
.gutreigns-ending-stats {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin: 1rem 0;
}
.gutreigns-ending-stat-item { text-align: center; }
.gutreigns-ending-stat-value {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.3rem;
  font-weight: 700;
}
.gutreigns-ending-stat-label {
  font-size: 0.65rem;
  color: var(--color-muted);
  text-transform: uppercase;
}

/* ============================================
   MISC
   ============================================ */
.gutreigns-hint {
  text-align: center;
  font-size: 0.78rem;
  color: var(--color-muted);
  margin: 0.3rem 0;
  opacity: 0.6;
}

.gutreigns-dotbar {
  display: flex;
  gap: 2px;
  margin-bottom: 0.5rem;
}
.gutreigns-dot {
  flex: 1;
  height: 5px;
  background-color: rgba(255,255,255,0.04);
  border-radius: 3px;
  transition: background-color 0.3s ease;
}
.gutreigns-dot.active { background-color: var(--color-muted); }
.stat-health .gutreigns-dot.active { background-color: var(--color-danger); }
.stat-immune .gutreigns-dot.active { background-color: var(--color-info); }
.stat-sanity .gutreigns-dot.active { background-color: var(--color-success); }
.stat-money .gutreigns-dot.active { background-color: var(--color-warning); }
.gutreigns-dotbar.critical .gutreigns-dot.active { animation: critPulse 1.5s infinite; }

.gutreigns-btn > button { min-height: 44px; }

/* ============================================
   STREAMLIT NATIVE OVERRIDES (Warning, Info, etc)
   ============================================ */
[data-testid="stAlert"] {
  background: rgba(100,181,246,0.06) !important;
  border: 1px solid rgba(100,181,246,0.15) !important;
  border-radius: var(--radius-md) !important;
  color: var(--color-text) !important;
}
.stProgress > div > div {
  background-color: rgba(255,255,255,0.06) !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--color-accent), var(--color-info)) !important;
}

/* Link buttons  */
.stLinkButton > a {
  background: var(--color-card-bg) !important;
  color: var(--color-text) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  transition: all 0.25s ease !important;
}
.stLinkButton > a:hover {
  background: var(--color-card-bg-hover) !important;
  border-color: var(--color-accent) !important;
  box-shadow: 0 0 12px rgba(212,165,116,0.2) !important;
  transform: translateY(-1px) !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
  color: var(--color-text) !important;
}

/* Tables */
.stTable, [data-testid="stTable"] {
  background: var(--color-card-bg) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden;
}
.stTable th {
  background: rgba(212,165,116,0.08) !important;
  color: var(--color-accent) !important;
  font-weight: 700 !important;
}
.stTable td {
  color: var(--color-text) !important;
  border-color: var(--color-border) !important;
}
.stTable tr:hover td {
  background: rgba(255,255,255,0.02) !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
  font-family: 'Noto Serif TC', serif !important;
  color: var(--color-accent) !important;
}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {
  color: var(--color-muted) !important;
}

/* Subheader */
[data-testid="stSubheader"] h2, [data-testid="stSubheader"] h3 {
  color: var(--color-primary) !important;
  font-family: 'Noto Serif TC', serif !important;
}

/* ============================================
   DISCLAIMER PAGE — Premium first impression
   ============================================ */
.stTitle {
  font-family: 'Noto Serif TC', serif !important;
  color: var(--color-primary) !important;
  letter-spacing: 0.05em !important;
}

/* ============================================
   MOBILE RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .main .block-container { padding-top: 0.5rem; padding-bottom: 1rem; }
  .gutreigns-title { font-size: 1.3rem; }
  .gutreigns-stat-row { gap: 1.2rem; }
  .gutreigns-stat-icon { width: 28px; height: 28px; font-size: 1.2rem; }
  .gutreigns-stat-fill { height: 32px; }
  .gutreigns-dialogue { font-size: 0.95rem; }
  .gutreigns-btn > button { width: 100%; min-height: 50px; font-size: 1rem; }
  .gutreigns-ending-title { font-size: 1.2rem; }
}

/* ============================================
   A11y: REDUCED MOTION
   ============================================ */
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition-duration: 0.01ms !important;
  }
}
/* ============================================
   RESTORED / MISSING CLASSES (Round 2 Fixes)
   ============================================ */
.gutreigns-privacy-panel {
  background: rgba(129, 199, 132, 0.08); /* flex with --color-success */
  border: 1px solid rgba(129, 199, 132, 0.3);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
}
.gutreigns-budget-panel {
  background: rgba(100, 181, 246, 0.08); /* flex with --color-info */
  border: 1px solid rgba(100, 181, 246, 0.3);
  border-radius: var(--radius-md);
  padding: 0.8rem;
  margin-bottom: 1rem;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes deathShake { 
  0% { transform: translate(1px, 1px) rotate(0deg); }
  10% { transform: translate(-1px, -2px) rotate(-1deg); } 
  20% { transform: translate(-3px, 0px) rotate(1deg); } 
  30% { transform: translate(3px, 2px) rotate(0deg); } 
  40% { transform: translate(1px, -1px) rotate(1deg); } 
  50% { transform: translate(-1px, 2px) rotate(-1deg); } 
  60% { transform: translate(-3px, 1px) rotate(0deg); } 
  70% { transform: translate(3px, 1px) rotate(-1deg); } 
  80% { transform: translate(-1px, -1px) rotate(1deg); } 
  90% { transform: translate(1px, 2px) rotate(0deg); } 
  100% { transform: translate(1px, -2px) rotate(-1deg); } 
}
@keyframes deathFlash { 0% { background-color: #4a0000; } 100% { background-color: var(--color-bg); } }
.death-screen { animation: deathFlash 0.5s ease-out, deathShake 0.5s; padding: 1rem; border-radius: var(--radius-lg); background: rgba(30,10,10,0.6); }

.animate-enter { animation: fadeIn 0.4s ease-out forwards; }
.card-enter { animation: fadeIn 0.3s ease-out; }
.season-transition { animation: fadeIn 0.5s ease-in-out; }
.gutreigns-title-icon { display: inline-block; animation: fadeIn 0.8s ease-out; margin-right: 0.5rem; }
</style>
"""
