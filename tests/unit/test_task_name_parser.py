from impossiblebench.report.data_loader import parse_task_display_name


def test_aleval_livecodebench_minimal():
    parsed = parse_task_display_name("aleval_livecodebench_minimal")
    assert parsed["dataset"] == "livecodebench"
    assert parsed["variant"] == "conflicting"
    assert parsed["agent_type"] == "minimal"


def test_aleval_livecodebench_tools():
    parsed = parse_task_display_name("aleval_livecodebench_tools")
    assert parsed["dataset"] == "livecodebench"
    assert parsed["variant"] == "conflicting"
    assert parsed["agent_type"] == "tools"


def test_aleval_swebench_minimal():
    parsed = parse_task_display_name("aleval_swebench_minimal")
    assert parsed["dataset"] == "swebench"
    assert parsed["variant"] == "conflicting"
    assert parsed["agent_type"] == "minimal"


def test_aleval_swebench_tools():
    parsed = parse_task_display_name("aleval_swebench_tools")
    assert parsed["dataset"] == "swebench"
    assert parsed["variant"] == "conflicting"
    assert parsed["agent_type"] == "tools"
