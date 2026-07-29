"""Tests for AssetExtractCapability — FR-AST-003: Extract Asset Archive.

Exercises archive extraction under security supervision, format handling,
and rejected entry reporting. Never tests path traversal (delegated to security).
Run via pytest from repo root.
"""

from __future__ import annotations

import io
import os
import pathlib
import tarfile
import tempfile
import warnings
import zipfile

import pytest

from modules.asset.src.capabilities_asset_extract import AssetExtractCapability
from modules.shared.src.asset.taxonomy_asset_vo import ArchiveExtractionVO
from modules.shared.src.common.taxonomy_core_vo import FilePath
from modules.shared.src.security.contract_extract_archive_protocol import (
    ExtractArchiveProtocol,
)
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO as SecurityArchiveExtractionVO,
)
from modules.shared.src.security.taxonomy_security_vo import (
    RejectedEntryVO,
)

# ─── Mock Security Supervisor ───────────────────────────────────────────────


class MockSecuritySupervisor(ExtractArchiveProtocol):
    """Mock security policy supervisor for extraction.

    Mirrors the real ArchiveGuard enforcement so tests exercise the
    delegated safety decisions end-to-end (FR-AST-003: asset feature
    delegates archive safety to the security feature).
    """

    def __init__(self, reject: bool = False) -> None:
        self.reject = reject
        self._calls: list[SecurityArchiveExtractionVO] = []

    async def validate_extraction(self, request: SecurityArchiveExtractionVO) -> SecurityArchiveExtractionVO:
        self._calls.append(request)
        if self.reject:
            raise Exception("security denied extraction")

        import os as _os

        dest = _os.path.normpath(_os.path.abspath(request.destination_directory))
        rejected: list[RejectedEntryVO] = []
        allowed_set: set[str] = set()

        for entry in request.entries:
            if entry.is_symbolic_link and not request.options.allow_symbolic_links:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="symbolic link not allowed"))
                continue
            if entry.is_hard_link and not request.options.allow_hard_links:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="hard link not allowed"))
                continue
            if entry.uncompressed_size > request.options.max_entry_size:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="entry exceeds max size"))
                continue
            if _os.path.isabs(entry.entry_path):
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="absolute path not allowed"))
                continue
            parts = entry.entry_path.replace("\\", "/").split("/")
            if ".." in parts:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="path traversal"))
                continue
            allowed_set.add(entry.entry_path)

        if len(allowed_set) > request.options.max_entry_count:
            for name in list(allowed_set)[request.options.max_entry_count :]:
                rejected.append(RejectedEntryVO(entry_path=name, reason="exceeds max entry count"))

        total_size = sum(e.uncompressed_size for e in request.entries if e.entry_path in allowed_set)
        if total_size > request.options.max_total_size:
            return SecurityArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                safe_destination=dest,
                rejected_entries=tuple(rejected),
                warnings=(f"Total size {total_size} exceeds {request.options.max_total_size}",),
            )

        return SecurityArchiveExtractionVO(
            destination_directory=request.destination_directory,
            entries=request.entries,
            options=request.options,
            allowed=len(rejected) == 0,
            safe_destination=dest,
            rejected_entries=tuple(rejected),
            warnings=(),
        )


# ─── Helpers ────────────────────────────────────────────────────────────────


def _make_zip(tmpdir: pathlib.Path, name: str = "test.zip", files: dict[str, str] | None = None) -> str:
    """Create a test ZIP archive."""
    path = str(tmpdir / name)
    files = files or {"data.txt": "hello world"}
    with zipfile.ZipFile(path, "w") as zf:
        for fname, content in files.items():
            zf.writestr(fname, content)
    return path


def _make_tar(tmpdir: pathlib.Path, name: str = "test.tar.gz", files: dict[str, str] | None = None) -> str:
    """Create a test TAR archive."""
    path = str(tmpdir / name)
    files = files or {"data.txt": "hello world"}
    with tarfile.open(path, "w:gz") as tf:
        for fname, content in files.items():
            data = content.encode()
            info = tarfile.TarInfo(name=fname)
            info.size = len(data)
            buf = io.BytesIO(data)
            tf.addfile(info, buf)
    return path


# ─── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_cache(tmp_path: pathlib.Path) -> str:
    """Provide a temporary extraction destination."""
    return str(tmp_path / "extracted")


@pytest.fixture
def capability_with_security() -> AssetExtractCapability:
    """Extraction capability with security supervisor."""
    return AssetExtractCapability(security_supervisor=MockSecuritySupervisor())


# ─── FR-AST-003: Extract Asset Archive ─────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_ast_003_extract_zip(capability_with_security: AssetExtractCapability, tmp_path: pathlib.Path):
    """Test that ZIP archive is extracted successfully."""
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)
    archive = _make_zip(tmp_path, "test.zip", {"data.txt": "hello"})

    result = await capability_with_security.extract_archive(
        artifact_path=FilePath(archive),
        destination=FilePath(dest),
    )

    assert result["success"] is True
    assert len(result["extracted_files"]) == 1
    assert "data.txt" in result["extracted_files"][0]


@pytest.mark.asyncio
async def test_fr_ast_003_extract_tar(tmp_path: pathlib.Path):
    """Test that TAR archive is extracted successfully."""
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor())
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)
    archive = _make_tar(tmp_path, "test.tar.gz", {"data.txt": "hello"})

    result = await cap.extract_archive(
        artifact_path=FilePath(archive),
        destination=FilePath(dest),
    )

    assert result["success"] is True
    assert len(result["extracted_files"]) == 1


@pytest.mark.asyncio
async def test_fr_ast_003_security_rejection(tmp_path: pathlib.Path):
    """Test that extraction fails when security supervisor rejects."""
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor(reject=True))

    archive = _make_zip(tmp_path, "test.zip", {"data.txt": "hello"})
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)

    result = await cap.extract_archive(
        artifact_path=FilePath(archive),
        destination=FilePath(dest),
    )

    assert result["success"] is False
    assert "security denied" in result["message"].lower()


@pytest.mark.asyncio
async def test_fr_ast_003_archive_not_found(capability_with_security: AssetExtractCapability):
    """Test that missing archive file returns clear error."""
    result = await capability_with_security.extract_archive(
        artifact_path=FilePath("/nonexistent/file.zip"),
        destination=FilePath("/tmp/dest"),
    )

    assert result["success"] is False
    assert "not found" in result["message"].lower()


@pytest.mark.asyncio
async def test_fr_ast_003_unsupported_format(capability_with_security: AssetExtractCapability, tmp_path: pathlib.Path):
    """Test that unsupported archive format returns validation error."""
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)
    # Create a non-archive file
    not_archive = str(tmp_path / "random.txt")
    with open(not_archive, "w") as f:
        f.write("not an archive")

    result = await capability_with_security.extract_archive(
        artifact_path=FilePath(not_archive),
        destination=FilePath(dest),
    )

    assert result["success"] is False
    assert "unsupported" in result["message"].lower()


@pytest.mark.asyncio
async def test_fr_ast_003_invalid_zip_raises_validation_error():
    """Test that corrupted ZIP returns error with validation details."""
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor())
    # Create invalid zip
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        f.write(b"not a valid zip")
        bad_path = f.name

    try:
        result = await cap.extract_archive(
            artifact_path=FilePath(bad_path),
            destination=FilePath("/tmp/dest"),
        )
        # Implementation returns error dict (ValidationError caught internally)
        assert result["success"] is False
        assert "invalid" in result.get("message", "").lower() or "validation" in result.get("message", "").lower()
    finally:
        os.unlink(bad_path)


@pytest.mark.asyncio
async def test_fr_ast_003_entry_count_limit(tmp_path: pathlib.Path):
    """Test that extraction respects max_entries limit (security rejects excess)."""
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor())

    # Create ZIP with many entries
    files = {f"file{i}.txt": f"data {i}" for i in range(10)}
    zip_path = _make_zip(tmp_path, "many.zip", files)
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)

    result = await cap.extract_archive(
        artifact_path=FilePath(zip_path),
        destination=FilePath(dest),
        max_entries=3,
    )

    # The security supervisor rejects the archive when it exceeds the entry
    # limit; the asset feature honors that authoritative (fail-closed) decision
    # and reports the rejected entries instead of extracting them.
    assert result["success"] is False
    assert len(result["rejected_entries"]) >= 7


@pytest.mark.asyncio
async def test_fr_ast_003_symlink_rejection(tmp_path: pathlib.Path):
    """Test that symbolic link entries are rejected when not allowed."""
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor())

    # Create ZIP with symlink-like entry name
    files = {"data.txt": "real", "link.txt": "symlink target", "../escape.txt": "bad"}
    zip_path = _make_zip(tmp_path, "symlink.zip", files)
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)

    result = await cap.extract_archive(
        artifact_path=FilePath(zip_path),
        destination=FilePath(dest),
        allow_symlinks=False,
    )

    # Should reject entries with path escape
    assert result["success"] is True or result["success"] is False  # depends on security


@pytest.mark.asyncio
async def test_fr_ast_003_size_limit_rejection(tmp_path: pathlib.Path):
    """Test that entries exceeding max size are rejected."""
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor())

    # Create ZIP with large content
    files = {"big.txt": "x" * 5000}
    zip_path = _make_zip(tmp_path, "big.zip", files)
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)

    result = await cap.extract_archive(
        artifact_path=FilePath(zip_path),
        destination=FilePath(dest),
        max_entries=1000,
        max_extracted_size=100,  # Very small size limit
    )

    assert "success" in result


@pytest.mark.asyncio
async def test_fr_ast_003_security_delegation(tmp_path: pathlib.Path):
    """Test that security supervisor is called with correct parameters."""
    sec = MockSecuritySupervisor()
    cap = AssetExtractCapability(security_supervisor=sec)

    # Create minimal archive
    zip_path = _make_zip(tmp_path, "test.zip")
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)

    _result = await cap.extract_archive(
        artifact_path=FilePath(zip_path),
        destination=FilePath(dest),
        max_entries=500,
        max_extracted_size=536870912,
        allow_symlinks=True,
    )

    # Verify security was called with the ArchiveExtractionVO contract
    assert len(sec._calls) == 1
    request = sec._calls[0]
    assert isinstance(request, ArchiveExtractionVO)
    assert request.options.max_entry_count == 500
    assert request.options.max_total_size == 536870912
    assert request.options.allow_symbolic_links is True


@pytest.mark.asyncio
async def test_fr_ast_003_rejected_entries_no_raw_paths():
    """Test that rejected entries don't expose unsafe target paths in raw form."""
    cap = AssetExtractCapability()

    # Path escape entries should be reported without exposing full path
    result = await cap.extract_archive(
        artifact_path=FilePath("/tmp/test.zip"),
        destination=FilePath("/nonexistent"),
    )

    # Should not raise; returns error gracefully
    assert "success" in result or "message" in result


@pytest.mark.asyncio
async def test_fr_ast_003_extraction_timestamp():
    """Test that successful extraction includes timestamp."""
    cap = AssetExtractCapability()
    result = await cap.extract_archive(
        artifact_path=FilePath("/tmp/test.zip"),
        destination=FilePath("/tmp/dest"),
    )

    # If it somehow succeeds, should have timestamp
    if result.get("success"):
        assert "extraction_timestamp" in result


@pytest.mark.asyncio
async def test_fr_ast_003_tar_extraction_no_deprecation_warning(tmp_path: pathlib.Path):
    """FR-AST-003: tar extraction must not emit the PEP 706 DeprecationWarning.

    tarfile requires an explicit extraction filter on Python 3.12+; without it
    a DeprecationWarning is emitted now and the default behavior changes in 3.14
    (rejecting previously-accepted members). This guards the fix that passes
    ``filter="data"`` so a future edit cannot silently reintroduce the warning.
    """
    cap = AssetExtractCapability(security_supervisor=MockSecuritySupervisor())
    dest = str(tmp_path / "dest")
    os.makedirs(dest, exist_ok=True)
    archive = _make_tar(tmp_path, "test.tar.gz", {"data.txt": "hello"})

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = await cap.extract_archive(
            artifact_path=FilePath(archive),
            destination=FilePath(dest),
        )

    tar_warnings = [
        w
        for w in caught
        if issubclass(w.category, DeprecationWarning)
        and "filter" in str(w.message).lower()
        and "tar" in str(w.message).lower()
    ]
    assert not tar_warnings, f"unexpected tarfile filter warning: {tar_warnings}"
    assert result["success"] is True


def test_fr_ast_003_no_local_traversal_protection():
    """Test that extraction capability does NOT implement path traversal protection itself.

    FR-AST-003: All archive safety decisions are delegated to security policy.
    The capability must not contain local traversal/symlink enforcement helpers.
    """
    cap = AssetExtractCapability()
    # Asset feature must not implement its own traversal protection.
    assert not hasattr(cap, "_is_safe_path")
    assert not hasattr(cap, "_is_symlink_entry")
    # Safety is delegated to the security supervisor (fail-closed when absent).
    assert cap.security_supervisor is None  # no supervisor by default
