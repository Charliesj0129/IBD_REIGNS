from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


FORBIDDEN_KEYS = {"name", "email", "phone", "address", "id_number", "raw_text"}


class AnalyticsError(ValueError):
    pass


@dataclass
class AnalyticsEvent:
    name: str
    payload: Dict[str, Any]
    timestamp: float


@dataclass
class AnalyticsSchema:
    required: Dict[str, List[str]]

    def validate(self, event: AnalyticsEvent) -> None:
        if event.name not in self.required:
            raise AnalyticsError("Unknown event")
        missing = [key for key in self.required[event.name] if key not in event.payload]
        if missing:
            raise AnalyticsError(f"Missing fields: {missing}")
        for key in event.payload.keys():
            if key in FORBIDDEN_KEYS:
                raise AnalyticsError("Forbidden field present")


class AnalyticsSink:
    def available(self) -> bool:
        return True

    def send(self, event: AnalyticsEvent) -> None:
        raise NotImplementedError


class InMemorySink(AnalyticsSink):
    def __init__(self) -> None:
        self.events: List[AnalyticsEvent] = []
        self._available = True

    def set_available(self, available: bool) -> None:
        self._available = available

    def available(self) -> bool:
        return self._available

    def send(self, event: AnalyticsEvent) -> None:
        self.events.append(event)


class JsonlSink(AnalyticsSink):
    def __init__(self, path: str) -> None:
        self.path = path

    def send(self, event: AnalyticsEvent) -> None:
        record = {"name": event.name, "timestamp": event.timestamp, **event.payload}
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")


@dataclass
class AnalyticsClient:
    schema: AnalyticsSchema
    sink: AnalyticsSink
    session_id: str
    buffer: List[AnalyticsEvent] = field(default_factory=list)

    def emit(self, name: str, payload: Dict[str, Any]) -> bool:
        event = AnalyticsEvent(name=name, payload={**payload, "session_id": self.session_id}, timestamp=time.time())
        try:
            self.schema.validate(event)
        except AnalyticsError:
            return False
        if self.sink.available():
            self.sink.send(event)
            return True
        self.buffer.append(event)
        return True

    def flush(self) -> None:
        if not self.sink.available():
            return
        while self.buffer:
            event = self.buffer.pop(0)
            self.sink.send(event)


def default_schema() -> AnalyticsSchema:
    return AnalyticsSchema(
        required={
            "session_start": ["session_id"],
            "session_end": ["session_id", "ending_id", "weeks_survived"],
            "card_shown": ["session_id", "card_id", "week", "pool", "available_options"],
            "option_chosen": ["session_id", "card_id", "option_side", "week", "stat_direction", "tags_count"],
            "consult_used": ["session_id", "card_id", "sanity_cost"],
            "education_shown": ["session_id", "education_id", "card_id"],
            "cta_clicked": ["session_id", "ending_id", "cta_type"],
            "autopsy_shown": ["session_id", "top_mistakes", "contributing_cards"],
        }
    )
