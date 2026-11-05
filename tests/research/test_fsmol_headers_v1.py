import io
import tarfile

from tools.index_fsmol_archive_v1 import inspect, unsafe_name


def test_headers_do_not_read_or_extract_assay_contents(tmp_path, monkeypatch):
    archive = tmp_path / "example.tar"
    with tarfile.open(archive, "w") as handle:
        row = tarfile.TarInfo("train/CHEMBL1.jsonl.gz")
        data = b"sentinel hidden outcomes must not be parsed"
        row.size = len(data)
        handle.addfile(row, io.BytesIO(data))

    def forbidden(*args, **kwargs):
        raise AssertionError("Member content was requested")

    monkeypatch.setattr(tarfile.TarFile, "extractfile", forbidden)
    monkeypatch.setattr(tarfile.TarFile, "extract", forbidden)
    monkeypatch.setattr(tarfile.TarFile, "extractall", forbidden)
    result = inspect(archive)
    assert result["status"] == "PASS_HEADER_AUDIT"
    assert result["member_count"] == 1
    assert not result["member_content_read"] and not result["extracted"]
    assert list(tmp_path.iterdir()) == [archive]


def test_reject_paths_links_and_resource_excess(tmp_path):
    for path in ("../escape", "/tmp/outside", "C:outside", "a\\..\\b", "safe/x:y"):
        assert unsafe_name(path)
    assert not unsafe_name("./train/CHEMBL1.jsonl.gz")
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as handle:
        row = tarfile.TarInfo("../escape")
        row.type = tarfile.SYMTYPE
        row.linkname = "/outside"
        handle.addfile(row)
    result = inspect(archive)
    assert result["status"] == "FAIL_HEADER_AUDIT"
    assert result["issues"][0]["reason"] == "UNSAFE_PATH_OR_ENTRY"


def test_member_and_stored_byte_caps_are_enforced(tmp_path):
    archive = tmp_path / "many.tar"
    with tarfile.open(archive, "w") as handle:
        for name in ("a", "b"):
            row = tarfile.TarInfo(name)
            row.size = 4
            handle.addfile(row, io.BytesIO(b"data"))
    assert inspect(archive, max_members=1)["issues"][0]["reason"] == "MEMBER_COUNT_CAP"
    assert inspect(archive, max_member_bytes=3)["issues"][0]["reason"] == "MEMBER_SIZE_CAP"
    assert inspect(archive, max_total_bytes=3)["issues"][0]["reason"] == "TOTAL_MEMBER_BYTES_CAP"
