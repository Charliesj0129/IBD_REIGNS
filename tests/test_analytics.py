from ibd_reigns.analytics import AnalyticsClient, AnalyticsSchema, InMemorySink, default_schema


def test_emit_valid_event():
    sink = InMemorySink()
    client = AnalyticsClient(schema=default_schema(), sink=sink, session_id="s1")
    ok = client.emit("session_start", {})
    assert ok is True
    assert sink.events[0].payload["session_id"] == "s1"


def test_emit_invalid_event_missing_fields():
    sink = InMemorySink()
    schema = AnalyticsSchema(required={"x": ["y"]})
    client = AnalyticsClient(schema=schema, sink=sink, session_id="s1")
    ok = client.emit("x", {})
    assert ok is False


def test_buffer_and_flush():
    sink = InMemorySink()
    sink.set_available(False)
    client = AnalyticsClient(schema=default_schema(), sink=sink, session_id="s1")
    client.emit("session_start", {})
    assert client.buffer
    sink.set_available(True)
    client.flush()
    assert not client.buffer
    assert len(sink.events) == 1


def test_privacy_forbidden_key():
    sink = InMemorySink()
    client = AnalyticsClient(schema=default_schema(), sink=sink, session_id="s1")
    ok = client.emit("session_start", {"name": "x"})
    assert ok is False
