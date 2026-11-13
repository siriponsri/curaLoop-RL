"""Source-interface regression; no reference answer or candidate model output."""

import numpy as np
import pytest

from research.local_agent_eval_v1.native_result import decode_native_result


@pytest.mark.parametrize(
    "flag,expected", [(True, True), (False, False), (1, True), (0, False), (np.bool_(True), True)]
)
def test_upstream_tuple_flag_is_used_instead_of_tuple_truthiness(flag, expected):
    value = decode_native_result((flag, "Native detail retained separately"))
    assert value["success"] is expected
    assert value["native_log_info"] == "Native detail retained separately"


@pytest.mark.parametrize(
    "value", [True, False, None, (1,), (0, "detail", "extra"), (0.5, "partial"), ("true", "text")]
)
def test_unsupported_native_contract_is_not_a_scientific_failure(value):
    with pytest.raises(ValueError):
        decode_native_result(value)
