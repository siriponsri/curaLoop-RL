"""Retain the old guard and derive a dedicated guard within the released 2 GiB cap."""
from pathlib import Path

source = Path(__file__).with_name("cf2p_guard_v1.py")
target = source.with_name("dc2_local_guard_v1.py")
assert not target.exists()
text = source.read_text(encoding="utf-8")
assert text.count("1073741824") == 2
target.write_text(text.replace("1073741824", "2147483648").replace("this fresh product/design release", "the local-workflow release (2 GiB ceiling)"), encoding="utf-8")
print("Dedicated guard created; historical source unchanged")
