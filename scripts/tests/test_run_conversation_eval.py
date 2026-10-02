from run_conversation_eval import completed_turns


def test_legacy_recheck_cannot_skip_primary_form_pair():
    records = [{"kind": "turn", "phase": phase, "case_id": "c03", "arm": "after_form",
                "repetition": 0, "status": "idle"} for phase in ("legacy_recheck", "recheck")]
    assert completed_turns(records, "finish") == []
    records.append(records[0] | {"phase": "finish"})
    assert completed_turns(records, "finish") == [["c03", "after_form", 0]]


def test_resume_does_not_skip_failed_turn_or_read_prepared_row_as_turn():
    records = [{"kind": "prepared", "case_id": "c01"},
               {"kind": "turn", "phase": "finish", "case_id": "c01", "arm": "after_form",
                "repetition": 0, "status": "failed"}]
    assert completed_turns(records, "finish") == []
