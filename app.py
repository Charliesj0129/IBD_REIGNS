from __future__ import annotations

import html
import random
import uuid

import streamlit as st
import streamlit.components.v1 as components

from ibd_reigns.analytics import AnalyticsClient, JsonlSink, default_schema
from ibd_reigns.analytics_summary import load_events, summarize_all, summarize_session
from ibd_reigns.constants import (
    FINAL_WEEK,
    FLARE_TAG,
    MALNUTRITION_TAG,
    REMISSION_BUFF_TAG,
    SLEEP_DEPRIVED_TAG,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_MONEY,
    STAT_SANITY,
    STEROID_MOON_FACE_TAG,
)
from ibd_reigns.cta import build_cta
from ibd_reigns.deck import CardDeck, apply_text_overrides
from ibd_reigns.engine import (
    apply_choice,
    build_autopsy_report,
    check_milestone_education,
    generate_contextual_education,
    generate_micro_tip,
    new_game_state,
    next_card,
    resolve_turn,
    run_end_of_year,
    season_pool_for_week,
    start_turn,
    EDUCATION_SEVERITY_COLORS,
)
from ibd_reigns.schema import load_cards, load_endings, load_game_rules
from ibd_reigns.ui import StreamlitRenderer
from ibd_reigns.ui.swipe import swipe_card_component
from ibd_reigns.ui_styles import MOBILE_CSS
from ibd_reigns.sql_engine import SqlEngine

def check_disclaimer() -> bool:
    if "accepted_disclaimer" not in st.session_state:
        st.session_state.accepted_disclaimer = False
    if not st.session_state.accepted_disclaimer:
        st.title("免責聲明")
        st.warning("請詳細閱讀以下條款再開始。")
        st.markdown("1. 非醫療建議：本遊戲僅供衛教與娛樂用途。\n2. 模擬性質：數值為玩法調整，非真實統計。\n3. 隱私保護：不蒐集個人資料。")
        agree = st.button("我已了解並同意開始", type="primary", use_container_width=True)
        if agree:
            st.session_state.accepted_disclaimer = True
            if "analytics" in st.session_state:
                st.session_state.analytics.emit("session_start", {})
                st.session_state.analytics.flush()
            st.rerun()
        return False
    return True


def init_state(cards, endings):
    if "state" not in st.session_state:
        st.session_state.state = new_game_state()
        st.session_state.cards = cards
        st.session_state.endings = endings
        st.session_state.deck = CardDeck(cards, rules=load_game_rules("assets/game_rules.json"))
        st.session_state.active_card = None
    if "analytics" not in st.session_state:
        session_id = str(uuid.uuid4())
        st.session_state.analytics = AnalyticsClient(
            schema=default_schema(),
            sink=JsonlSink("/tmp/gut_reigns_analytics.jsonl"),
            session_id=session_id,
        )
    if "sql_engine" not in st.session_state:
        st.session_state.sql_engine = SqlEngine("gut_reigns.db")


def render_swipe_tutorial() -> None:
    """Show a one-time swipe tutorial before the first card."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:75vh;text-align:center;padding:1rem;">
      <div style="font-size:2.5rem;margin-bottom:0.5rem;">👑</div>
      <div style="font-size:1.6rem;font-weight:700;color:#E8D5B7;margin-bottom:0.8rem;
                  font-family:'Noto Serif TC',serif;">腸道王權</div>
      <div style="font-size:1.1rem;color:#E8D5B7;margin-bottom:2.5rem;line-height:1.6;">
        你剛診斷出 IBD (發炎性腸道疾病)，<br>請在日常生活中做出對你最好的選擇。
      </div>

      <!-- 動態教學區塊 -->
      <div class="tutorial-anim-container">
        <!-- 模擬卡片 -->
        <div class="tutorial-card">
          <div style="font-size:3rem;">🃏</div>
        </div>
        <!-- 模擬手指 -->
        <div class="tutorial-hand">👆</div>
        
        <!-- 文字提示 -->
        <div class="tutorial-text tutorial-text-left">拒絕 👈</div>
        <div class="tutorial-text tutorial-text-right">👉 接受</div>
      </div>

      <div style="font-size:1rem;color:#8A7A6A;line-height:1.8;margin-top:2.5rem;margin-bottom:1.5rem;background:rgba(232,213,183,0.05);padding:1rem;border-radius:12px;border:1px solid rgba(232,213,183,0.1);">
        <strong style="color:#E8D5B7;font-size:1.1rem;">操作說明</strong><br>
        1. 按住畫面的卡片，<strong>往左</strong>或<strong>往右</strong>滑動<br>
        2. 或者，直接點擊下方的<strong>紅色 / 綠色按鈕</strong>
      </div>
    </div>
    
    <style>
      .tutorial-anim-container {
        position: relative;
        width: 250px;
        height: 200px;
        margin: 0 auto;
        perspective: 1000px;
      }
      .tutorial-card {
        position: absolute;
        top: 20px;
        left: 75px;
        width: 100px;
        height: 140px;
        background: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        z-index: 2;
        animation: swipeCycle 4s infinite cubic-bezier(0.4, 0, 0.2, 1);
        transform-origin: bottom center;
      }
      .tutorial-hand {
        position: absolute;
        top: 80px;
        left: 110px;
        font-size: 3rem;
        z-index: 3;
        animation: handCycle 4s infinite cubic-bezier(0.4, 0, 0.2, 1);
        filter: drop-shadow(0 4px 4px rgba(0,0,0,0.5));
      }
      .tutorial-text {
        position: absolute;
        top: 80px;
        font-size: 1.2rem;
        font-weight: 700;
        opacity: 0;
        z-index: 1;
      }
      .tutorial-text-left {
        left: 0px;
        color: var(--color-danger);
        animation: textLeftCycle 4s infinite cubic-bezier(0.4, 0, 0.2, 1);
      }
      .tutorial-text-right {
        right: 0px;
        color: var(--color-success);
        animation: textRightCycle 4s infinite cubic-bezier(0.4, 0, 0.2, 1);
      }

      /* 重複 4 秒的動畫週期：0-2秒右滑，2-4秒左滑 */
      @keyframes handCycle {
        0%, 15% { transform: translate(0, 0) scale(1); } /* 停在中間 */
        15.1% { transform: translate(0, 0) scale(0.9); } /* 點下 */
        35% { transform: translate(60px, 0) scale(0.9); } /* 往右拖 */
        40% { transform: translate(60px, 0) scale(1); opacity: 1; } /* 放開 */
        45%, 50% { transform: translate(60px, 0) scale(1); opacity: 0; } /* 消失 */
        
        50.1%, 65% { transform: translate(0, 0) scale(1); opacity: 1; } /* 回到中間出現 */
        65.1% { transform: translate(0, 0) scale(0.9); } /* 點下 */
        85% { transform: translate(-60px, 0) scale(0.9); } /* 往左拖 */
        90% { transform: translate(-60px, 0) scale(1); opacity: 1; } /* 放開 */
        95%, 100% { transform: translate(-60px, 0) scale(1); opacity: 0; } /* 消失 */
      }
      
      @keyframes swipeCycle {
        0%, 15% { transform: translate(0, 0) rotate(0deg); }
        35% { transform: translate(60px, 0) rotate(10deg); }
        40%, 50% { transform: translate(0, 0) rotate(0deg); }
        
        50.1%, 65% { transform: translate(0, 0) rotate(0deg); }
        85% { transform: translate(-60px, 0) rotate(-10deg); }
        90%, 100% { transform: translate(0, 0) rotate(0deg); }
      }

      @keyframes textRightCycle {
        0%, 20% { opacity: 0; transform: translateX(-10px); }
        35%, 45% { opacity: 1; transform: translateX(0); }
        50%, 100% { opacity: 0; }
      }
      @keyframes textLeftCycle {
        0%, 70% { opacity: 0; transform: translateX(10px); }
        85%, 95% { opacity: 1; transform: translateX(0); }
        100% { opacity: 0; }
      }
    </style>
    """, unsafe_allow_html=True)
    if st.button("▶ 開始遊戲", type="primary", use_container_width=True):
        st.session_state.tutorial_shown = True
        st.rerun()


def render_dotbar(value: int, key: str = "default") -> None:
    active = max(0, min(10, int(round(value / 10))))
    critical = "critical" if value < 20 else ""
    dots = "".join(
        "<span class='gutreigns-dot active'></span>" if i < active else "<span class='gutreigns-dot'></span>"
        for i in range(10)
    )
    st.markdown(f"<div class='gutreigns-dotbar stat-{key.lower()} {critical}'>{dots}</div>", unsafe_allow_html=True)


def render_progress_bar(week: int) -> None:
    """Render week/season progress bar."""
    progress_pct = min(100, int((week / FINAL_WEEK) * 100))
    season_names = {"spring": "🌸 春", "summer": "☀️ 夏", "fall": "🍂 秋", "winter": "❄️ 冬"}
    current_season = season_pool_for_week(week)
    season_label = season_names.get(current_season, current_season)
    st.markdown(f"""
    <div class="gutreigns-progress-wrap">
      <div class="gutreigns-progress-label">
        <span>第 {week} 週</span>
        <span>{season_label} · {progress_pct}%</span>
      </div>
      <div class="gutreigns-progress-bar">
        <div class="gutreigns-progress-fill" style="width: {progress_pct}%;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


_TAG_BADGE_MAP = {
    FLARE_TAG: ("🔥 發炎中", "flare"),
    STEROID_MOON_FACE_TAG: ("🌕 月亮臉", "moon-face"),
    SLEEP_DEPRIVED_TAG: ("😴 睡眠不足", "sleep-deprived"),
    "ANEMIA": ("🩸 貧血", "anemia"),
    REMISSION_BUFF_TAG: ("✨ 黏膜修復中", "remission"),
    "STEROID_DEPENDENT": ("💊 類固醇依賴", "steroid-dep"),
    "POST_SURGERY": ("🏥 術後恢復", "post-surgery"),
    MALNUTRITION_TAG: ("⚠️ 營養不良", "anemia"),  # reuse anemia style
}


def render_status_badges(tags: set) -> None:
    """Show active status effects as colored badges."""
    badges = []
    for tag, (label, css_class) in _TAG_BADGE_MAP.items():
        if tag in tags:
            badges.append(f"<span class='gutreigns-badge {css_class}'>{label}</span>")
    if badges:
        st.markdown(f"<div class='gutreigns-status-bar'>{''.join(badges)}</div>", unsafe_allow_html=True)


def render_education(card) -> None:
    """Render education popup if card has education data."""
    if not card.education:
        return
    edu = card.education
    title = html.escape(edu.title)
    content = html.escape(edu.content)
    source = html.escape(edu.source) if edu.source else ""
    source_html = f"<div class='gutreigns-edu-source'>📚 {source}</div>" if source else ""
    st.markdown(f"""
    <div class="gutreigns-edu">
      <div class="gutreigns-edu-title">📖 {title}</div>
      <div class="gutreigns-edu-content">{content}</div>
      {source_html}
    </div>
    """, unsafe_allow_html=True)


def render_education_from_dict(edu: dict) -> None:
    """Render education from a dict (used for deferred/post-choice education)."""
    title = html.escape(edu.get("title", ""))
    content = html.escape(edu.get("content", ""))
    source = edu.get("source", "")
    source_html = f"<div class='gutreigns-edu-source'>📚 {html.escape(source)}</div>" if source else ""
    st.markdown(f"""
    <div class="gutreigns-edu">
      <div class="gutreigns-edu-title">📖 {title}</div>
      <div class="gutreigns-edu-content">{content}</div>
      {source_html}
    </div>
    """, unsafe_allow_html=True)


def render_ending_screen(ending, state) -> None:
    """Render a rich visual ending screen."""
    is_good = ending.cta_type == "good"
    tier_class = "good" if is_good else "bad"
    emoji = "🌟" if ending.tier == "top" else "✅" if is_good else "💔"
    title = html.escape(ending.title)
    desc = html.escape(ending.description)

    stat_items = ""
    stat_colors = {STAT_HEALTH: "#E57373", STAT_IMMUNE: "#64B5F6", STAT_SANITY: "#81C784", STAT_MONEY: "#FFB74D"}
    stat_labels = {STAT_HEALTH: "健康", STAT_IMMUNE: "免疫", STAT_SANITY: "心理", STAT_MONEY: "經濟"}
    for stat in (STAT_HEALTH, STAT_IMMUNE, STAT_SANITY, STAT_MONEY):
        val = state.stats.get(stat, 0)
        color = stat_colors[stat]
        label = stat_labels[stat]
        stat_items += f"""
        <div class="gutreigns-ending-stat-item">
          <div class="gutreigns-ending-stat-value" style="color:{color}">{val}</div>
          <div class="gutreigns-ending-stat-label">{label}</div>
        </div>"""

    weeks_survived = min(state.week, FINAL_WEEK)
    st.markdown(f"""
    <div class="gutreigns-ending {tier_class}">
      <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{emoji}</div>
      <div class="gutreigns-ending-title">{title}</div>
      <div class="gutreigns-ending-desc">{desc}</div>
      <div class="gutreigns-ending-stats">{stat_items}
        <div class="gutreigns-ending-stat-item">
          <div class="gutreigns-ending-stat-value" style="color:#7F8C8D">{weeks_survived}</div>
          <div class="gutreigns-ending-stat-label">存活週數</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_sparkline(history: list, color: str = "#999", width: int = 80, height: int = 20) -> str:
    """Generate a compact inline SVG sparkline from a stat history list."""
    if len(history) < 2:
        return ""
    min_val = max(0, min(history) - 5)
    max_val = max(100, max(history) + 5)
    val_range = max_val - min_val or 1
    n = len(history)
    points = []
    for i, val in enumerate(history[-20:]):  # last 20 data points
        x = int(i / (min(n, 20) - 1) * width) if min(n, 20) > 1 else 0
        y = height - int((val - min_val) / val_range * height)
        points.append(f"{x},{y}")
    polyline = " ".join(points)
    return (
        f"<svg width='{width}' height='{height}' style='vertical-align:middle;margin-left:8px'>"
        f"<polyline points='{polyline}' fill='none' stroke='{color}' stroke-width='1.5' "
        f"stroke-linecap='round' stroke-linejoin='round'/></svg>"
    )


_DEATH_LABELS = {
    "sepsis": "🦠 敗血症",
    "perforation": "💥 腸穿孔",
    "megacolon": "⚠️ 巨結腸症",
    "bad_dropout": "💭 放棄治療",
    "bad_bankruptcy": "💸 經濟崩潰",
    "financial_toxicity": "💸 經濟毒性",
}


def render_autopsy_report(state) -> None:
    """Render structured post-mortem analysis on game over."""
    report = build_autopsy_report(state)

    def safe_str(s):
        # Remove any surrogate characters that Python's strict utf-8 codec rejects
        return "".join(c for c in str(s) if not (0xD800 <= ord(c) <= 0xDFFF))

    fatal_label = safe_str(_DEATH_LABELS.get(report["fatal_stat"], f"☠️ {report['fatal_stat']}"))

    cards_html = ""
    for c in report["worst_cards"]:
        cards_html += (
            f"<div style='display:flex;justify-content:space-between;padding:3px 0;"
            f"border-bottom:1px solid rgba(0,0,0,0.05);font-size:0.82rem'>"
            f"<span>第 {c['week']} 週 · <b>{html.escape(c['card_id'])}</b></span>"
            f"<span style='color:#C0392B'>{c['delta']:+d}</span></div>"
        )
    cards_html = safe_str(cards_html)

    # Counterfactual HTML
    cf_html = ""
    for cf in report.get("counterfactuals", []):
        side_label = "⬅️ 左" if cf["chose"] == "left" else "➡️ 右"
        cf_html += (
            f"<div style='font-size:0.8rem;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.05)'>"
            f"W{cf['week']} <b>{html.escape(cf['card_id'])}</b> — "
            f"你選了{side_label} (影響: {cf['actual_delta']:+d})</div>"
        )
    cf_html = safe_str(cf_html)

    # Education learned HTML
    edu_learned = report.get("education_learned", [])
    total_topics = 11
    edu_progress_pct = int(len(edu_learned) / total_topics * 100) if total_topics else 0

    eims_html = safe_str(", ".join(report["active_eims"]) if report["active_eims"] else "無")
    no_data_html = safe_str('<span style="font-size:0.82rem;color:var(--color-muted)">無資料</span>')

    st.markdown(safe_str(f"""
    <div class="gutreigns-edu" style="border-left-color:#C0392B; background:rgba(192,57,43,0.04);">
      <div class="gutreigns-edu-title" style="color:#C0392B">🔍 惡化原因分析</div>
      <div style="margin:0.5rem 0">
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem">{fatal_label}</div>
      </div>
      <div style="font-size:0.78rem;color:var(--color-muted);margin-bottom:0.4rem">— 主要負面事件 —</div>
      <div style="margin-bottom:0.6rem">{cards_html or no_data_html}</div>
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap;font-size:0.82rem">
        <div>💊 藥物順從性: <b>{report['adherence_pct']}%</b></div>
        <div>🧪 類固醇使用: <b>{report['steroid_uses']} 次</b></div>
        <div>🩺 活躍共病: <b>{eims_html}</b></div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    # Counterfactual "What If" panel
    if cf_html:
        st.markdown(safe_str(f"""
        <div class="gutreigns-edu" style="border-left-color:#F39C12; background:rgba(243,156,18,0.04);">
          <div class="gutreigns-edu-title" style="color:#F39C12">🔮 如果你選了另一邊…</div>
          {cf_html}
        </div>
        """), unsafe_allow_html=True)

    # Education progress
    if edu_learned:
        topics_html = "".join(f"<span style='display:inline-block;background:rgba(76,175,80,0.15);border:1px solid rgba(76,175,80,0.3);border-radius:8px;padding:2px 8px;margin:2px;font-size:0.75rem'>✅ {html.escape(t)}</span>" for t in edu_learned)
        st.markdown(safe_str(f"""
        <div class="gutreigns-edu" style="border-left-color:#4CAF50; background:rgba(76,175,80,0.04);">
          <div class="gutreigns-edu-title" style="color:#4CAF50">📚 IBD 知識進度 ({edu_progress_pct}%)</div>
          <div style="margin-top:0.4rem">{topics_html}</div>
        </div>
        """), unsafe_allow_html=True)


def render_preview(label: str, deltas: dict, advanced: bool) -> None:
    st.markdown(f"**{label}**")
    if not deltas:
        st.caption("0")
        return
    for stat, delta in deltas.items():
        name = {"HEALTH": "黏膜", "IMMUNE": "免疫", "SANITY": "心智", "MONEY": "資本"}.get(stat, stat)
        if advanced:
            sign = "+" if delta > 0 else ""
            st.write(f"{name}: {sign}{delta}")
        else:
            magnitude = abs(delta)
            tier = "小" if magnitude <= 5 else "中" if magnitude <= 15 else "大"
            st.write(f"{name}: {tier}")
            if magnitude >= 20:
                st.markdown("<div class='gutreigns-risk'>⚠️ 高風險</div>", unsafe_allow_html=True)


def render_icon(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _preview_lines(preview: dict, advanced: bool) -> list[str]:
    lines = []
    if not preview:
        return ["0"]
    for stat, value in preview.items():
        label = {"HEALTH": "黏膜", "IMMUNE": "免疫", "SANITY": "心智", "MONEY": "資本"}.get(stat, stat)
        if advanced:
            sign = "+" if value > 0 else ""
            lines.append(f"{label} {sign}{value}")
        else:
            magnitude = abs(value)
            tier = "小" if magnitude <= 5 else "中" if magnitude <= 15 else "大"
            lines.append(f"{label} {tier}")
    return lines


def render_medical_profile(state) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🩺 醫療檔案")
    
    # Diet Score
    diet_map = {-10: "🤢 毒性", -5: "🍟 垃圾", 0: "😐 普通", 5: "🥗 健康", 10: "🤩 超級"}
    score = state.diet_score
    label = min(diet_map.items(), key=lambda x: abs(x[0] - score))[1]
    st.sidebar.metric("飲食評分", f"{score}", label)
    
    # Ostomy
    if "OSTOMY_BAG" in state.tags:
        st.sidebar.markdown("### ♻️ 造口護理")
        skill = state.ostomy_care_skill
        st.sidebar.progress(skill / 10.0, text=f"熟練度: {skill}/10")
        
    # Medications
    meds = []
    if state.biologic_uses:
        meds.append(f"生物製劑: {sum(state.biologic_uses.values())} 劑")
    if state.steroid_use_count > 0:
        meds.append(f"類固醇: {state.steroid_use_count} 次")
    
    if meds:
        st.sidebar.markdown("**用藥紀錄:**")
        for m in meds:
            st.sidebar.caption(f"• {m}")
            
    # Social Status
    if "ISOLATED" in state.tags:
        st.sidebar.error("⚠️ 社交孤立 (SANITY 上限降低)")
        
    # Milestones
    if state.milestones:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📅 大事記:**")
        for m in state.milestones[:5]:
            st.sidebar.caption(f"• {m}")

    # IBD Knowledge Progress (7 contextual + 4 milestones = 11)
    total_topics = 11
    learned = len(state.learned_topics)
    if learned > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📚 IBD 知識:**")
        st.sidebar.progress(min(1.0, learned / total_topics), text=f"{learned}/{total_topics} 知識點")
        if learned >= total_topics:
            st.sidebar.markdown(
                '<div style="text-align:center;background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,183,77,0.1));'
                'border:1px solid rgba(255,215,0,0.3);border-radius:12px;padding:0.5rem;margin-top:0.3rem">'
                '<span style="font-size:1.3rem">🏆</span><br>'
                '<span style="font-size:0.75rem;font-weight:700;color:#FFD700">IBD 知識大師</span>'
                '</div>',
                unsafe_allow_html=True,
            )


def render_analytics_dashboard() -> None:
    from ibd_reigns.analytics_summary import (
        purge_old_events, PrivacyBudgetTracker, filter_by_consent,
        CONSENT_LEVELS, summarize_trend,
        load_events, summarize_all
    )

    st.subheader("📊 數據總結")

    # --- Consent Level Selector ---
    consent = st.radio(
        "📋 資料同意等級",
        CONSENT_LEVELS,
        index=2,
        format_func=lambda x: {"basic": "🟢 基本 (僅總數)", "analytics": "🟡 分析 (卡片+結局)", "full": "🔴 完整 (全部資料)"}[x],
        horizontal=True,
        key="dashboard_consent"
    )

    events = load_events("/tmp/gut_reigns_analytics.jsonl")
    summary = summarize_all(events, consent_level=consent)
    summary = filter_by_consent(summary, consent)
    pm = summary.get("privacy_metadata", {})

    # --- Privacy Budget Tracker ---
    if "privacy_budget" not in st.session_state:
        st.session_state.privacy_budget = PrivacyBudgetTracker()
    budget = st.session_state.privacy_budget
    budget.record_query()

    # --- Privacy Posture Panel ---
    minimized_text = ", ".join(pm.get("fields_minimized", []))
    budget_info = budget.to_dict()
    st.markdown(f"""
    <div style="background:rgba(76,175,80,0.08);border:1px solid rgba(76,175,80,0.3);
                border-radius:12px;padding:1rem;margin-bottom:1rem;">
      <div style="font-weight:700;color:#4CAF50;margin-bottom:0.5rem;">🔒 隱私保護狀態</div>
      <div style="display:flex;flex-wrap:wrap;gap:1rem;font-size:0.85rem;">
        <div>機制: <b>{pm.get('mechanism', 'N/A')}</b></div>
        <div>ε (epsilon): <b>{pm.get('epsilon', 'N/A')}</b></div>
        <div>k-匿名門檻: <b>{pm.get('k_anonymity_threshold', 'N/A')}</b></div>
        <div>資料保留: <b>{pm.get('data_retention_days', 90)} 天</b></div>
        <div>同意等級: <b>{consent}</b></div>
      </div>
      <div style="margin-top:0.5rem;font-size:0.75rem;color:#8A7A6A;">
        最小化欄位: {minimized_text}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Privacy Budget Visual ---
    st.markdown(f"""
    <div style="background:rgba(100,181,246,0.08);border:1px solid rgba(100,181,246,0.3);
                border-radius:12px;padding:0.8rem;margin-bottom:1rem;">
      <div style="font-weight:700;color:#64B5F6;margin-bottom:0.4rem;">📊 隱私預算 (Epsilon Budget)</div>
      <div style="height:8px;background:rgba(255,255,255,0.08);border-radius:4px;overflow:hidden;margin-bottom:0.4rem;">
        <div style="height:100%;width:{budget_info['utilization_pct']}%;background:linear-gradient(90deg,#4CAF50,#FFB74D,#E57373);border-radius:4px;transition:width 0.3s;"></div>
      </div>
      <div style="display:flex;gap:1.5rem;font-size:0.8rem;color:#8A7A6A;">
        <div>已使用: <b>{budget_info['spent']}ε</b> / {budget_info['total_budget']}ε</div>
        <div>剩餘: <b>{budget_info['remaining']}ε</b></div>
        <div>查詢次數: <b>{budget_info['query_count']}</b></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Metrics ---
    col1, col2 = st.columns(2)
    if "total_events" in summary:
        col1.metric("總事件數 (DP)", summary["total_events"])
    col2.metric("總玩家數 (DP)", summary.get("total_sessions", "N/A"))

    # --- Weekly Trend Chart ---
    st.subheader("📈 每週玩家趨勢 (DP)")
    trend = summarize_trend(events)
    if any(t["sessions"] > 0 for t in trend):
        import pandas as pd
        df = pd.DataFrame(trend)
        st.bar_chart(df, x="week", y="sessions", color="#4CAF50")
    else:
        st.caption("尚無足夠趨勢資料")

    if "top_cards" in summary:
        st.subheader("🃏 最常見事件")
        if summary["top_cards"]:
            st.table([{"card_id": card, "count (DP)": count} for card, count in summary["top_cards"]])
        else:
            st.caption("尚無資料")

    if "endings" in summary:
        st.subheader("🏁 結局分佈")
        if summary["endings"]:
            st.table([{"ending": ending, "count (DP)": count} for ending, count in summary["endings"]])
        else:
            st.caption("尚無資料")

    if "education_engagement" in summary:
        st.subheader("📚 衛教觸發統計")
        edu = summary.get("education_engagement", [])
        if edu:
            st.table([{"教育主題": eid, "觸發次數 (DP)": cnt} for eid, cnt in edu])
        else:
            st.caption("尚未觸發任何衛教內容")

    # =====================================================================
    # 細緻化玩家關卡決策分析 (Fine-grained Event Analytics)
    # =====================================================================
    if consent in ("analytics", "full"):
        from ibd_reigns.event_analytics import (
            compute_card_decision_stats,
            compute_behavioral_funnel,
            compute_survival_by_choice,
            find_critical_decision_cards,
        )

        st.markdown("---")
        st.subheader("🎯 行為漏斗分析 (DP)")

        funnel = compute_behavioral_funnel(events, apply_dp=True)
        if funnel:
            max_count = max((f["count"] for f in funnel), default=1) or 1
            funnel_html = ""
            for i, stage in enumerate(funnel):
                bar_pct = min(100, int(stage["count"] / max_count * 100))
                # 漸變色：從綠色到紅色
                hue = int(120 * (1 - i / max(len(funnel) - 1, 1)))
                color = f"hsl({hue}, 65%, 55%)"
                funnel_html += f"""
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;">
                  <div style="min-width:140px;font-size:0.8rem;text-align:right;color:#999;">{html.escape(stage['stage'])}</div>
                  <div style="flex:1;height:22px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
                    <div style="height:100%;width:{bar_pct}%;background:{color};border-radius:4px;transition:width 0.5s;"></div>
                  </div>
                  <div style="min-width:60px;font-size:0.75rem;color:#bbb;">{stage['count']} ({stage['percent']}%)</div>
                </div>"""
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.03);border:1px solid rgba(0,0,0,0.06);
                        border-radius:12px;padding:1rem;margin-bottom:1rem;">
              {funnel_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("尚無足夠行為漏斗資料")

        # --- Per-Card Decision Stats ---
        st.markdown("---")
        st.subheader("🃏 單卡決策比例 (DP)")
        card_stats = compute_card_decision_stats(events, apply_dp=True)
        if card_stats:
            top_cards = card_stats[:15]  # 顯示前 15 張
            cards_html = ""
            for cs in top_cards:
                lr = cs.get("left_ratio")
                rr = cs.get("right_ratio")
                left_pct = int((lr or 0) * 100)
                right_pct = int((rr or 0) * 100)
                cards_html += f"""
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;
                            padding:0.4rem 0.6rem;border-bottom:1px solid rgba(0,0,0,0.04);">
                  <div style="min-width:120px;font-size:0.78rem;font-weight:600;">{html.escape(cs['card_id'])}</div>
                  <div style="flex:1;display:flex;height:16px;border-radius:3px;overflow:hidden;">
                    <div style="width:{left_pct}%;background:#5B8DEF;transition:width 0.3s;" title="← {left_pct}%"></div>
                    <div style="width:{right_pct}%;background:#EF5B5B;transition:width 0.3s;" title="→ {right_pct}%"></div>
                  </div>
                  <div style="min-width:90px;font-size:0.7rem;color:#888;">← {left_pct}% / {right_pct}% →</div>
                  <div style="min-width:30px;font-size:0.7rem;color:#aaa;">n={cs['total_chosen']}</div>
                </div>"""
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.02);border:1px solid rgba(0,0,0,0.06);
                        border-radius:12px;padding:0.8rem;">
              <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#bbb;padding:0 0.6rem 0.4rem;">
                <span>卡牌 ID</span><span>← 左 / 右 →</span>
              </div>
              {cards_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("尚無足夠決策資料（需至少 5 次出現）")

        # --- Critical Decision Cards ---
        if card_stats:
            critical = find_critical_decision_cards(card_stats, threshold_ratio=0.3)
            if critical:
                st.markdown("---")
                st.subheader("⚠️ 嚴苛選項分析 (左右差異 ≥ 30%)")
                crit_html = ""
                for cc in critical[:10]:
                    dominant_label = "⬅️ 大多選左" if cc["dominant_side"] == "left" else "➡️ 大多選右"
                    diff_pct = int(cc["ratio_diff"] * 100)
                    crit_html += f"""
                    <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;
                                border-bottom:1px solid rgba(0,0,0,0.04);font-size:0.8rem;">
                      <span style="min-width:120px;font-weight:600;">{html.escape(cc['card_id'])}</span>
                      <span style="color:#F39C12;font-weight:700;">Δ{diff_pct}%</span>
                      <span style="color:#888;">{dominant_label}</span>
                    </div>"""
                st.markdown(f"""
                <div style="background:rgba(243,156,18,0.05);border:1px solid rgba(243,156,18,0.2);
                            border-radius:12px;padding:0.8rem;">
                  {crit_html}
                </div>
                """, unsafe_allow_html=True)

        # --- Survival Rate by Choice ---
        survival = compute_survival_by_choice(events, apply_dp=True)
        if survival:
            st.markdown("---")
            st.subheader("📈 選擇與存活率差異 (DP)")
            survival_rows = []
            for s in survival[:10]:
                survival_rows.append({
                    "卡牌": s["card_id"],
                    "← 左存活率": f"{int((s['left_survivors'] or 0) * 100)}%" if s["left_survivors"] is not None else "—",
                    "→ 右存活率": f"{int((s['right_survivors'] or 0) * 100)}%" if s["right_survivors"] is not None else "—",
                    "← 左平均週數": s["left_avg_weeks"] if s["left_avg_weeks"] is not None else "—",
                    "→ 右平均週數": s["right_avg_weeks"] if s["right_avg_weeks"] is not None else "—",
                    "存活率差 (左-右)": f"{int((s['delta_survival'] or 0) * 100)}%" if s["delta_survival"] is not None else "—",
                })
            st.table(survival_rows)

    st.markdown("---")
    st.subheader("🗑️ 資料管理")
    if st.button("清除超過 90 天的舊資料", type="secondary"):
        purged = purge_old_events("/tmp/gut_reigns_analytics.jsonl")
        st.success(f"已清除 {purged} 筆過期資料")


def main() -> None:
    if not check_disclaimer():
        return
    cards = load_cards(["assets/events.json", "assets/scenarios_expansion.json"])
    endings = {ending.id: ending for ending in load_endings("assets/endings.json")}
    init_state(cards, endings)

    # Show swipe tutorial before the first game
    if not st.session_state.get("tutorial_shown", False):
        render_swipe_tutorial()
        return

    state = st.session_state.state
    deck = st.session_state.deck
    analytics = st.session_state.analytics
    renderer = StreamlitRenderer()

    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    # Removed sidebar mode selector to keep analytics hidden
    render_medical_profile(state)
    
    start_turn(state)


    # --- Game Over Screen ---
    if state.game_over:
        st.markdown(MOBILE_CSS, unsafe_allow_html=True)
        st.markdown('<div class="death-screen">', unsafe_allow_html=True)
        endings = st.session_state.endings
        ending_id = state.death_reason or "unknown"
        ending = endings.get(ending_id)
        if ending:
            render_ending_screen(ending, state)
        else:
            st.error(f"遊戲結束：{ending_id}")
        render_autopsy_report(state)
        renderer.cta(build_cta(ending.cta_type if ending else "bad_end"))
        
        # Record run
        if not getattr(state, "_run_recorded", False):
            st.session_state.sql_engine.record_run(state.week, ending.id if ending else ending_id, ending_id)
            state._run_recorded = True

        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("📊 查看全球玩家數據"):
            render_analytics_dashboard()

        if st.button("🔄 重新開始", use_container_width=True, type="primary"):
            del st.session_state.state
            st.rerun()
        return

    pool = season_pool_for_week(state.week)
    if state.week > FINAL_WEEK:
        ending = run_end_of_year(state, endings)
        analytics.emit("session_end", {"ending_id": ending.id, "weeks_survived": state.week})
        analytics.emit(
            "autopsy_shown",
            {
                "top_mistakes": [r.card_id for r in state.history[-3:]],
                "contributing_cards": [r.card_id for r in state.history[-5:]],
            },
        )
        analytics.flush()

        st.markdown(MOBILE_CSS, unsafe_allow_html=True)
        render_ending_screen(ending, state)
        renderer.cta(build_cta(ending.cta_type or ending.id))

        if not getattr(state, "_run_recorded", False):
            st.session_state.sql_engine.record_run(state.week, ending.id, "survived")
            state._run_recorded = True

        events = load_events("/tmp/gut_reigns_analytics.jsonl")
        session_summary = summarize_session(events, analytics.session_id)
        with st.expander("📊 本局數據總結"):
            st.json(session_summary)
        
        with st.expander("🌍 查看全球趨勢"):
            render_analytics_dashboard()

        share_html = """
        <div style="margin-top:0.8rem; text-align:center;">
          <button id="copyLink" style="padding:0.6rem 1.2rem; border-radius:12px; border:1px solid rgba(0,0,0,0.1); background:white; font-weight:600; cursor:pointer; transition:all 0.2s"
            onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='white'">📋 複製連結</button>
        </div>
        <script>
          const btn = document.getElementById('copyLink');
          btn.addEventListener('click', () => {
            navigator.clipboard.writeText(window.location.href);
            btn.innerText = '✅ 已複製';
            setTimeout(() => btn.innerText = '📋 複製連結', 2000);
          });
        </script>
        """
        components.html(share_html, height=80)
        return

    if state.active_card_id:
        try:
            card = deck.get_card(state.active_card_id)
        except KeyError:
            state.active_card_id = None
            card = next_card(state, deck, random.random, pool)
            state.active_card_id = card.id
    else:
        card = next_card(state, deck, random.random, pool)
        state.active_card_id = card.id

    # --- Header: Title + Progress ---
    any_crit = any(state.stats.get(s, 50) < 20 for s in [STAT_HEALTH, STAT_IMMUNE, STAT_SANITY, STAT_MONEY])
    title_icon = "💀" if any_crit else "👑"
    icon_class = "critical" if any_crit else ""
    st.markdown(f"<div class='gutreigns-title'><span class='gutreigns-title-icon {icon_class}'>{title_icon}</span> 腸道王權</div>", unsafe_allow_html=True)
    st.markdown("<div class='gutreigns-ornament'></div>", unsafe_allow_html=True)

    # Season transition detection
    prev_season = st.session_state.get('_prev_season')
    if prev_season and prev_season != pool:
        st.markdown('<div class="season-transition">', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-size:1.5rem;padding:0.5rem;opacity:0.8">🌿 季節轉換 → {pool.upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.session_state._prev_season = pool

    render_progress_bar(state.week)

    # --- Status Badges ---
    render_status_badges(state.tags)

    # --- Reigns-style stat pillars are now inside the swipe component ---

    # --- Card ---
    text = card.text
    text = apply_text_overrides(card, state.tags, base_text=text)
    character_line = ""
    if card.character_name or card.character_role:
        name = card.character_name or ""
        role = card.character_role or ""
        character_line = f"{name} {role}".strip()

    locks = deck.options_locked(state, card)
    # --- Resolve Dynamic SVGs ---
    def get_character_svg(role: str, name: str) -> str:
        role_map = {
            "doctor.svg": ["醫師", "主治", "doctor"],
            "nurse.svg": ["護理", "護士", "病房", "nurse"],
            "boss.svg": ["主管", "經理", "老闆", "boss", "manager"],
            "colleague.svg": ["同事", "上班", "colleague"],
            "family.svg": ["家人", "親戚", "媽媽", "爸爸", "梅嬸", "family"],
            "friend.svg": ["朋友", "病友", "論壇", "friend", "夥伴", "傳言"],
            "inner_voice.svg": ["內心", "自我", "疲憊", "衝動", "voice"],
            "treatment.svg": ["藥師", "照護團隊"],
            "system.svg": ["急診", "突發", "系統"]
        }
        search_text = f"{role} {name}".lower()
        for svg, keywords in role_map.items():
            if any(k in search_text for k in keywords):
                return svg
        return "default.svg"

    svg_name = get_character_svg(card.character_role or "", card.character_name or "")
    silhouette = render_icon(f"assets/characters/{svg_name}")
    
    # Render Swipe Component (HTML Bridge)
    swipe_result = swipe_card_component(
        card.id,
        character_line,
        text,
        card.left.label,
        card.right.label,
        card.left.effect,
        card.right.effect,
        state.stats,
        silhouette,
        season=pool,
        week=state.week,
    )

    # --- Education: show PREVIOUS card's education (teaching moment after choice) ---
    pending_edu = st.session_state.get("pending_education")
    if pending_edu:
        severity = pending_edu.get("severity", "info")
        color, bg, icon = EDUCATION_SEVERITY_COLORS.get(severity, EDUCATION_SEVERITY_COLORS["info"])
        st.markdown(f"""
        <div class="gutreigns-edu" style="border-left-color:{color}; background:{bg};">
          <div class="gutreigns-edu-title" style="color:{color}">{icon} {html.escape(pending_edu.get('title', ''))}</div>
          <div class="gutreigns-edu-content">{html.escape(pending_edu.get('content', ''))}</div>
          <div class="gutreigns-edu-source">— {html.escape(pending_edu.get('source', ''))}</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.pending_education = None

    # --- Micro-Tip ---
    tip = generate_micro_tip(state)
    if tip:
        st.markdown(f'<div style="text-align:center;font-size:0.72rem;color:#8A7A6A;opacity:0.7;margin:0.3rem 0;font-style:italic">{html.escape(tip)}</div>', unsafe_allow_html=True)

    left = False
    right = False
    st.markdown("<div style='margin-top:1.5rem;text-align:center;font-size:0.9rem;color:#8A7A6A;margin-bottom:0.5rem;'>不用滑動，點按鈕也可以👇</div>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        left = st.button(
            f"👈 {card.left.label}",
            disabled=locks.get("left") is not None,
            use_container_width=True,
            key="left",
            help=locks.get("left"),
        )
    with col_r:
        right = st.button(
            f"{card.right.label} 👉",
            disabled=locks.get("right") is not None,
            use_container_width=True,
            key="right",
            help=locks.get("right"),
        )
    
    # Custom CSS to enlarge the specific buttons based on their keys
    st.markdown("""
    <style>
      button[data-testid="baseButton-secondary"] {
        height: 60px !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        border-width: 2px !important;
        font-weight: bold !important;
      }
    </style>
    """, unsafe_allow_html=True)

    analytics.emit(
        "card_shown",
        {
            "card_id": card.id,
            "week": state.week,
            "pool": pool,
            "available_options": ["left", "right"],
        },
    )

    # Convert component result to logic
    swipe_left = False
    swipe_right = False
    if isinstance(swipe_result, dict) and swipe_result.get("week") == state.week:
        swipe_dir = swipe_result.get("direction")
        swipe_left = swipe_dir == "left"
        swipe_right = swipe_dir == "right"

    if left or right or swipe_left or swipe_right:
        swipe_choice = 'left' if (left or swipe_left) else 'right'
        option = card.left if swipe_choice == 'left' else card.right
        state.active_card_id = None
        
        # Apply choice and check for death/events
        resolve_turn(state, deck, card, option, random.random)
        
        analytics.emit(
            "option_chosen",
            {
                "card_id": card.id,
                "option_side": swipe_choice,
                "week": state.week,
                "stat_direction": {k: ("up" if v > 0 else "down") for k, v in option.effect.items() if v != 0},
                "tags_count": len(option.add_tags),
            },
        )
        
        # Store education for next turn (teaching moment)
        if card.education:
            st.session_state.pending_education = {
                "title": card.education.title,
                "content": card.education.content,
                "source": card.education.source,
                "severity": "info",
            }
        else:
            # 1. Check milestone education (first-time events)
            milestone_edu = check_milestone_education(state, card, option)
            if milestone_edu:
                st.session_state.pending_education = milestone_edu
                analytics.emit("education_shown", {
                    "education_id": milestone_edu["title"],
                    "card_id": card.id,
                })
            else:
                # 2. Contextual education: triggered by player state
                ctx_edu = generate_contextual_education(state, card, option)
                if ctx_edu:
                    st.session_state.pending_education = ctx_edu
                    analytics.emit("education_shown", {
                        "education_id": ctx_edu["title"],
                        "card_id": card.id,
                    })

        if state.game_over:
            ending_id = state.death_reason or "unknown"
            analytics.emit("session_end", {"ending_id": ending_id, "weeks_survived": state.week})
            analytics.emit(
                "autopsy_shown",
                {
                    "top_mistakes": [r.card_id for r in state.history[-3:]],
                    "contributing_cards": [r.card_id for r in state.history[-5:]],
                },
            )
            analytics.flush()
        
        st.rerun()


if __name__ == "__main__":
    main()
