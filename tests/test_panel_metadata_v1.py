import pytest

from research.preparation_v1.panel_audit import extract_task_ids


def test_official_task_enumeration_is_parsed_as_data_without_executing_code():
    source = "raise RuntimeError('must not execute')\nPCBA_TASKS = ['PCBA-2', 'PCBA-1']\n"
    assert extract_task_ids(source) == [1, 2]


@pytest.mark.parametrize(
    "source",
    [
        "PCBA_TASKS = list(range(10))",
        "PCBA_TASKS = ['PCBA-1', 'PCBA-1']",
        "PCBA_TASKS = ['https://example.org/data.csv']",
        "PCBA_TASKS = [1]",
    ],
)
def test_unknown_or_executable_remote_enumerations_are_rejected(source):
    with pytest.raises(ValueError):
        extract_task_ids(source)
