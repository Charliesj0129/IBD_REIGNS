from ibd_reigns.sql_engine import SqlEngine
import os

def test_sql_engine_lifecycle(tmp_path):
    db_path = tmp_path / "test.db"
    engine = SqlEngine(str(db_path))
    
    # Test Init
    assert os.path.exists(db_path)
    
    # Test Record Run
    engine.record_run(weeks=10, ending_id="bad_end", death_reason="infection")
    
    # Test Profile
    stats = engine.get_profile()
    assert stats["total_runs"] == 1
    assert stats["max_weeks"] == 10
    assert "bad_end" in stats["seen_endings"]
    assert stats["death_count"] == 1

    # Test Record another run (better)
    engine.record_run(weeks=52, ending_id="clinical_remission", death_reason="survived")
    stats = engine.get_profile()
    assert stats["total_runs"] == 2
    assert stats["max_weeks"] == 52
    assert "clinical_remission" in stats["seen_endings"]
