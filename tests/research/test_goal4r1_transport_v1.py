"""Engineering regression for the observed legacy two-receipt stdout reply."""

import json

import pytest

from tools.goal4r1_remote_v1 import decode_helper_output


def test_legacy_core_and_wrapper_receipts_are_both_retained():
    core, wrapper = {"status": "CORE_REMOVED"}, {"status": "TASK_AND_EXPORT_REMOVED"}
    result = decode_helper_output((json.dumps(core) + "\n" + json.dumps(wrapper) + "\n").encode())
    assert result["status"] == wrapper["status"]
    assert result["preceding_stdout_records"] == [core]
    assert result["stdout_json_record_count"] == 2
    assert decode_helper_output(json.dumps(wrapper).encode()) == wrapper
    with pytest.raises(json.JSONDecodeError):
        decode_helper_output((json.dumps(wrapper) + "\nnot-a-json-receipt").encode())
