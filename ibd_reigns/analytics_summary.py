import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List

# --- Differential Privacy Primitives ---

def laplace_noise(sensitivity: float = 1.0, epsilon: float = 1.0) -> float:
    """Generate Laplace noise for differential privacy.
    Lower epsilon = more privacy, more noise.
    """
    scale = sensitivity / epsilon
    u = random.random() - 0.5
    return -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))


def dp_count(true_count: int, epsilon: float = 0.5) -> int:
    """Return a differentially private count."""
    return max(0, round(true_count + laplace_noise(1.0, epsilon)))


# --- Data Retention ---

def purge_old_events(path: str, max_age_days: int = 90) -> int:
    """Remove events older than max_age_days. Returns number purged."""
    if not os.path.exists(path):
        return 0
    cutoff = time.time() - (max_age_days * 86400)
    kept = []
    purged = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("timestamp", 0) >= cutoff:
                    kept.append(line)
                else:
                    purged += 1
            except json.JSONDecodeError:
                purged += 1
    with open(path, "w", encoding="utf-8") as f:
        for line in kept:
            f.write(line + "\n")
    return purged


def load_events(path: str) -> List[Dict[str, Any]]:
    events = []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                events.append(json.loads(line))
    except FileNotFoundError:
        return []
    return events


def summarize_session(events: List[Dict[str, Any]], session_id: str) -> Dict[str, Any]:
    session_events = [e for e in events if e.get("session_id") == session_id]
    choices = [e for e in session_events if e.get("name") == "option_chosen"]
    cards = [e.get("card_id") for e in session_events if e.get("name") == "card_shown"]
    ending = next((e for e in session_events if e.get("name") == "session_end"), None)
    counts = Counter(cards)
    return {
        "session_id": session_id,
        "weeks_survived": ending.get("weeks_survived") if ending else None,
        "ending_id": ending.get("ending_id") if ending else None,
        "choices": len(choices),
        "most_seen_card": counts.most_common(1)[0][0] if counts else None,
        "unique_cards": len(counts),
    }


# --- k-Anonymity ---

K_ANONYMITY_THRESHOLD = 5  # Suppress categories with fewer than k entries


def k_anonymize(
    items: List[tuple], k: int = K_ANONYMITY_THRESHOLD
) -> List[tuple]:
    """Suppress rare categories to maintain k-anonymity.

    Items with count < k are merged into an 'other' bucket.
    """
    kept = []
    suppressed_count = 0
    for label, count in items:
        if count >= k:
            kept.append((label, count))
        else:
            suppressed_count += count
    if suppressed_count > 0:
        kept.append(("other (suppressed)", suppressed_count))
    return kept


def summarize_all(events: List[Dict[str, Any]], apply_dp: bool = True, consent_level: str = "full") -> Dict[str, Any]:
    """Aggregate summary with optional differential privacy noise and k-anonymity."""
    sessions = Counter(e.get("session_id") for e in events if e.get("session_id"))
    endings = Counter(e.get("ending_id") for e in events if e.get("name") == "session_end")
    cards = Counter(e.get("card_id") for e in events if e.get("name") == "card_shown")
    edu_events = [e for e in events if e.get("name") == "education_shown"]
    edu_cards = Counter(e.get("education_id") for e in edu_events)

    if apply_dp:
        dp_sessions = dp_count(len(sessions))
        dp_events = dp_count(len(events))
        dp_cards = k_anonymize([(card, dp_count(cnt)) for card, cnt in cards.most_common(10)])
        dp_endings = k_anonymize([(end, dp_count(cnt)) for end, cnt in endings.most_common()])
        dp_edu = k_anonymize([(eid, dp_count(cnt)) for eid, cnt in edu_cards.most_common(5)])
    else:
        dp_sessions = len(sessions)
        dp_events = len(events)
        dp_cards = cards.most_common(10)
        dp_endings = endings.most_common()
        dp_edu = edu_cards.most_common(5)

    return {
        "total_sessions": dp_sessions,
        "total_events": dp_events,
        "top_cards": dp_cards[:5],
        "endings": dp_endings,
        "education_engagement": dp_edu,
        "privacy_applied": apply_dp,
        "privacy_metadata": {
            "mechanism": "Laplace DP" if apply_dp else "none",
            "epsilon": 0.5 if apply_dp else None,
            "k_anonymity_threshold": K_ANONYMITY_THRESHOLD if apply_dp else None,
            "data_retention_days": 90,
            "fields_minimized": ["stat_direction (no raw deltas)", "tags_count (no tag names)"],
            "consent_level": consent_level,
        },
    }


# --- Privacy Budget Tracking ---

class PrivacyBudgetTracker:
    """Track cumulative epsilon spend across DP queries.

    Once the budget is exhausted, further DP queries return None
    to prevent excessive privacy loss.
    """

    def __init__(self, total_budget: float = 5.0, per_query_epsilon: float = 0.5) -> None:
        self.total_budget = total_budget
        self.per_query_epsilon = per_query_epsilon
        self.spent: float = 0.0
        self.query_count: int = 0

    def can_query(self) -> bool:
        return self.spent + self.per_query_epsilon <= self.total_budget

    def record_query(self) -> bool:
        """Record a query. Returns True if the query was allowed."""
        if not self.can_query():
            return False
        self.spent += self.per_query_epsilon
        self.query_count += 1
        return True

    def remaining(self) -> float:
        return max(0.0, self.total_budget - self.spent)

    def utilization_pct(self) -> int:
        return int(100 * self.spent / self.total_budget) if self.total_budget > 0 else 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_budget": self.total_budget,
            "spent": round(self.spent, 2),
            "remaining": round(self.remaining(), 2),
            "query_count": self.query_count,
            "utilization_pct": self.utilization_pct(),
        }


# --- Consent-Level Filtering ---

CONSENT_LEVELS = ("basic", "analytics", "full")


def filter_by_consent(summary: Dict[str, Any], consent_level: str) -> Dict[str, Any]:
    """Filter summary data based on user consent level.

    - basic: only total sessions (no card/event detail)
    - analytics: sessions + cards + endings + education (no raw events)
    - full: everything
    """
    if consent_level == "basic":
        return {
            "total_sessions": summary.get("total_sessions", 0),
            "privacy_applied": summary.get("privacy_applied"),
            "privacy_metadata": summary.get("privacy_metadata"),
        }
    elif consent_level == "analytics":
        filtered = dict(summary)
        filtered.pop("total_events", None)
        return filtered
    return summary


# --- Trend Data (DP-protected weekly sessions) ---

def summarize_trend(events: List[Dict[str, Any]], weeks: int = 8) -> List[Dict[str, Any]]:
    """Aggregate DP-protected session counts per calendar week.

    Returns a list of {week_label, sessions} for the last `weeks` weeks.
    """
    import datetime

    now = time.time()
    week_buckets: Dict[str, int] = {}

    for event in events:
        if event.get("name") != "session_start":
            continue
        ts = event.get("timestamp", 0)
        age_days = (now - ts) / 86400
        if age_days > weeks * 7:
            continue
        dt = datetime.datetime.fromtimestamp(ts)
        week_label = dt.strftime("W%V")
        week_buckets[week_label] = week_buckets.get(week_label, 0) + 1

    # Build sorted list for last N weeks
    trend = []
    for i in range(weeks - 1, -1, -1):
        dt = datetime.datetime.fromtimestamp(now - i * 7 * 86400)
        label = dt.strftime("W%V")
        raw = week_buckets.get(label, 0)
        trend.append({"week": label, "sessions": dp_count(raw)})

    return trend

