import json
from typing import Any, Dict, List, Union

from .models import Card, CardConditions, CardOption, Education, Ending

REQUIRED_CARD_FIELDS = {"id", "text", "left", "right"}
REQUIRED_OPTION_FIELDS = {"label", "effect"}
REQUIRED_ENDING_FIELDS = {"id", "title", "trigger", "description"}


class SchemaError(ValueError):
    pass


def _require_fields(data: Dict[str, Any], required: set, context: str) -> None:
    missing = required - set(data.keys())
    if missing:
        raise SchemaError(f"Missing fields in {context}: {sorted(missing)}")


def _coerce_option(data: Dict[str, Any]) -> CardOption:
    _require_fields(data, REQUIRED_OPTION_FIELDS, "CardOption")
    return CardOption(
        label=str(data["label"]),
        effect=dict(data.get("effect", {})),
        add_tags=list(data.get("add_tags", [])),
        remove_tags=list(data.get("remove_tags", [])),
        impact=data.get("impact"),
        response_text=data.get("response_text"),
        cost_money=data.get("cost_money"),
        consult_hint=data.get("consult_hint"),
        consult_cost_sanity=data.get("consult_cost_sanity"),
        toxic_delta=int(data.get("toxic_delta", 0)),
        symptom_suppression=bool(data.get("symptom_suppression", False)),
        steroid_use=bool(data.get("steroid_use", False)),
        stop_steroid=bool(data.get("stop_steroid", False)),
        biologic_id=data.get("biologic_id"),
        induction_start=bool(data.get("induction_start", False)),
        injection_required=bool(data.get("injection_required", False)),
        missed_injection=bool(data.get("missed_injection", False)),
        mild_treatment=bool(data.get("mild_treatment", False)),
        risk_tags=list(data.get("risk_tags", [])),
        risk_event_id=data.get("risk_event_id"),
        diet_delta=int(data.get("diet_delta", 0)),
        ostomy_skill_delta=int(data.get("ostomy_skill_delta", 0)),
    )


def _coerce_conditions(data: Dict[str, Any]) -> CardConditions:
    return CardConditions(
        min_week=data.get("min_week"),
        max_week=data.get("max_week"),
        min_immune=data.get("min_immune"),
        max_immune=data.get("max_immune"),
        required_tags=list(data.get("required_tags", [])),
        forbidden_tags=list(data.get("forbidden_tags", [])),
    )


def _coerce_education(data: Dict[str, Any]) -> Education:
    return Education(
        title=str(data.get("title", "")),
        content=str(data.get("content", "")),
        source=str(data.get("source", "")),
        image_url=data.get("image_url"),
    )


def load_cards(path: Union[str, List[str]]) -> List[Card]:
    paths = [path] if isinstance(path, str) else path
    cards: List[Card] = []
    
    for p in paths:
        with open(p, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, list):
            raise SchemaError(f"{p} must be a list")
            
        for item in raw:
            if not isinstance(item, dict):
                raise SchemaError("Card entry must be an object")
            _require_fields(item, REQUIRED_CARD_FIELDS, "Card")
            left = _coerce_option(item.get("left", {}))
            right = _coerce_option(item.get("right", {}))
            conditions = _coerce_conditions(item.get("conditions", {}))
            education = None
            if "education" in item:
                education = _coerce_education(item["education"])
            card = Card(
                id=str(item["id"]),
                text=str(item["text"]),
                left=left,
                right=right,
                emoji=item.get("emoji"),
                character_name=item.get("character_name"),
                character_role=item.get("character_role"),
                chain_next=list(item.get("chain_next", [])),
                theme=item.get("theme"),
                rarity=item.get("rarity"),
                conditions=conditions,
                weight=int(item.get("weight", 1)),
                education=education,
                hint_deceptive=bool(item.get("hint_deceptive", False)),
                educational=bool(item.get("educational", False)),
                consult_hint=item.get("consult_hint"),
                tags=list(item.get("tags", [])),
                text_overrides=dict(item.get("text_overrides", {})),
                forced=bool(item.get("forced", False)),
                only_one_option=bool(item.get("only_one_option", False)),
                pool=item.get("pool"),
            )
            cards.append(card)
    return cards


def load_endings(path: str) -> List[Ending]:
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, list):
        raise SchemaError("endings.json must be a list")
    endings: List[Ending] = []
    for item in raw:
        if not isinstance(item, dict):
            raise SchemaError("Ending entry must be an object")
        _require_fields(item, REQUIRED_ENDING_FIELDS, "Ending")
        endings.append(
            Ending(
                id=str(item["id"]),
                title=str(item["title"]),
                trigger=str(item["trigger"]),
                description=str(item["description"]),
                tier=item.get("tier"),
                cta_type=item.get("cta_type"),
            )
        )
    return endings


def load_game_rules(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
