from impossiblebench.analysis.data_loader import parse_task_display_name


def test_parse_task_display_name_livecodebench_tools():
    parsed = parse_task_display_name("lcb_conflicting_canmod_tools_callout")
    assert parsed["dataset"] == "livecodebench"
    assert parsed["variant"] == "conflicting"
    assert parsed["agent_type"] == "tools"


def test_parse_task_display_name_swebench_minimal():
    parsed = parse_task_display_name("swebench_oneoff_minimal_hide_reset_callout")
    assert parsed["dataset"] == "swebench"
    assert parsed["variant"] == "oneoff"
    assert parsed["agent_type"] == "minimal"
