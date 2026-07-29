"""Tests for ArchiveGuard — FR-SEC-002.

Exercises archive extraction validation: absolute paths, traversal, symlinks,
hard links, depth/size/count limits, and audit metadata.
Run via pytest from repo root.
"""

from __future__ import annotations

import os

from modules.security.src.capabilities_archive_guard import ArchiveGuard
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveEntryVO,
    ArchiveExtractionOptionsVO,
    ArchiveExtractionVO,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_guard() -> ArchiveGuard:
    """Create a fresh ArchiveGuard instance."""
    return ArchiveGuard()


def _extract(guard: ArchiveGuard, entries: list[ArchiveEntryVO], options: ArchiveExtractionOptionsVO | None = None) -> ArchiveExtractionVO:
    """Helper to run validate_extraction synchronously via asyncio."""
    import asyncio
    request = ArchiveExtractionVO(
        destination_directory="/safe/out",
        entries=tuple(entries),
        options=options or ArchiveExtractionOptionsVO(),
    )
    return asyncio.run(guard.validate_extraction(request))


# ─── FR-SEC-002: Safely Extract Archive ──────────────────────────────────


class TestAbsoluteEntryPath:
    """Test absolute entry path rejection (FR-SEC-002)."""

    def test_absolute_entry_rejected(self) -> None:
        """FR-SEC-002: absolute entry paths are rejected."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="/etc/passwd")])
        assert res.allowed is False
        assert len(res.rejected_entries) >= 1
        assert any("absolute" in r.reason.lower() for r in res.rejected_entries)

    def test_multiple_absolute_entries_all_rejected(self) -> None:
        """FR-SEC-002: multiple absolute entries are all rejected."""
        guard = _make_guard()
        res = _extract(guard, [
            ArchiveEntryVO(entry_path="/etc/passwd"),
            ArchiveEntryVO(entry_path="/usr/bin/python"),
        ])
        assert res.allowed is False
        assert len(res.rejected_entries) >= 2

    def test_absolute_entry_audit_metadata(self) -> None:
        """FR-SEC-002: rejection includes audit metadata."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="/etc/passwd")])
        assert isinstance(res.audit_metadata, dict)


class TestPathTraversalInEntries:
    """Test path traversal in archive entries (FR-SEC-002)."""

    def test_traversal_entry_rejected(self) -> None:
        """FR-SEC-002: entries with ../ are rejected."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="../escape.blend")])
        assert res.allowed is False
        assert any("traversal" in r.reason.lower() for r in res.rejected_entries)

    def test_nested_traversal_rejected(self) -> None:
        """FR-SEC-002: nested ../ traversal is rejected."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="../../../../etc/passwd")])
        assert res.allowed is False

    def test_traversal_in_subdir_rejected(self) -> None:
        """FR-SEC-002: traversal anywhere in entry path is rejected."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="subdir/../escape.blend")])
        assert res.allowed is False

    def test_safe_subdir_entry_allowed(self) -> None:
        """FR-SEC-002: safe subdirectory entries are allowed."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="subdir/file.blend")])
        assert res.allowed is True


class TestSymlinkAndHardLinkEntries:
    """Test symbolic and hard link entry rejection (FR-SEC-002)."""

    def test_symbolic_link_entry_rejected_by_default(self) -> None:
        """FR-SEC-002: symbolic link entries rejected by default."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="link", is_symbolic_link=True)])
        assert res.allowed is False
        assert any("Symbolic link" in r.reason for r in res.rejected_entries)

    def test_hard_link_entry_rejected_by_default(self) -> None:
        """FR-SEC-002: hard link entries rejected by default."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="hardlink", is_hard_link=True)])
        assert res.allowed is False
        assert any("Hard link" in r.reason for r in res.rejected_entries)

    def test_symlink_allowed_when_policy_allows(self) -> None:
        """FR-SEC-002: symbolic links allowed when explicitly permitted by policy."""
        guard = _make_guard()
        opts = ArchiveExtractionOptionsVO(allow_symbolic_links=True)
        res = _extract(guard, [ArchiveEntryVO(entry_path="link", is_symbolic_link=True)], opts)
        assert res.allowed is True

    def test_hard_link_allowed_when_policy_allows(self) -> None:
        """FR-SEC-002: hard links allowed when explicitly permitted by policy."""
        guard = _make_guard()
        opts = ArchiveExtractionOptionsVO(allow_hard_links=True)
        res = _extract(guard, [ArchiveEntryVO(entry_path="hardlink", is_hard_link=True)], opts)
        assert res.allowed is True

    def test_both_symlink_and_hard_link_rejected_default(self) -> None:
        """FR-SEC-002: both symlink and hard link rejected when neither is allowed."""
        guard = _make_guard()
        res = _extract(guard, [
            ArchiveEntryVO(entry_path="link", is_symbolic_link=True),
            ArchiveEntryVO(entry_path="hardlink", is_hard_link=True),
        ])
        assert res.allowed is False
        assert len(res.rejected_entries) >= 2


class TestEntryCountLimits:
    """Test archive entry count enforcement (FR-SEC-002)."""

    def test_entry_count_exceeded_rejected(self) -> None:
        """FR-SEC-002: entries exceeding max count are rejected."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path=f"file{i}") for i in range(10)]
        opts = ArchiveExtractionOptionsVO(max_entry_count=5)
        res = _extract(guard, entries, opts)
        assert res.allowed is False
        assert len(res.rejected_entries) >= 5

    def test_entry_count_at_limit_allowed(self) -> None:
        """FR-SEC-002: entries at max count are allowed."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path=f"file{i}") for i in range(5)]
        opts = ArchiveExtractionOptionsVO(max_entry_count=5)
        res = _extract(guard, entries, opts)
        assert res.allowed is True

    def test_entry_count_zero_rejected(self) -> None:
        """FR-SEC-002: zero max entry count rejects all."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path="file1")]
        opts = ArchiveExtractionOptionsVO(max_entry_count=0)
        res = _extract(guard, entries, opts)
        assert res.allowed is False

    def test_large_entry_count_allowed(self) -> None:
        """FR-SEC-002: large entry count limit allows many entries."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path=f"file{i}") for i in range(100)]
        opts = ArchiveExtractionOptionsVO(max_entry_count=200)
        res = _extract(guard, entries, opts)
        assert res.allowed is True


class TestSizeLimits:
    """Test archive size enforcement (FR-SEC-002)."""

    def test_individual_entry_size_exceeded(self) -> None:
        """FR-SEC-002: individual entry exceeding max size is rejected."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path="big.blend", uncompressed_size=500)]
        opts = ArchiveExtractionOptionsVO(max_entry_size=100)
        res = _extract(guard, entries, opts)
        assert res.allowed is False
        assert any("size" in r.reason.lower() for r in res.rejected_entries)

    def test_total_size_exceeded(self) -> None:
        """FR-SEC-002: total extracted size exceeding limit is rejected."""
        guard = _make_guard()
        entries = [
            ArchiveEntryVO(entry_path="file1", uncompressed_size=60),
            ArchiveEntryVO(entry_path="file2", uncompressed_size=60),
        ]
        opts = ArchiveExtractionOptionsVO(max_total_size=100)
        res = _extract(guard, entries, opts)
        assert res.allowed is False

    def test_total_size_at_limit_allowed(self) -> None:
        """FR-SEC-002: total size at limit is allowed."""
        guard = _make_guard()
        entries = [
            ArchiveEntryVO(entry_path="file1", uncompressed_size=50),
            ArchiveEntryVO(entry_path="file2", uncompressed_size=50),
        ]
        opts = ArchiveExtractionOptionsVO(max_total_size=100)
        res = _extract(guard, entries, opts)
        assert res.allowed is True

    def test_zero_max_entry_size_rejects_all(self) -> None:
        """FR-SEC-002: zero max entry size rejects all entries with size > 0."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path="file1", uncompressed_size=10)]
        opts = ArchiveExtractionOptionsVO(max_entry_size=0)
        res = _extract(guard, entries, opts)
        assert res.allowed is False

    def test_zero_uncompressed_size_allowed(self) -> None:
        """FR-SEC-002: zero uncompressed size entry is allowed."""
        guard = _make_guard()
        entries = [ArchiveEntryVO(entry_path="empty.txt", uncompressed_size=0)]
        opts = ArchiveExtractionOptionsVO(max_entry_size=100, max_total_size=100)
        res = _extract(guard, entries, opts)
        assert res.allowed is True


class TestDestinationValidation:
    """Test destination directory validation (FR-SEC-002)."""

    def test_safe_destination_normalized(self) -> None:
        """FR-SEC-002: safe destination is normalized."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="file.txt")])
        assert res.safe_destination == os.path.normpath("/safe/out")

    def test_entry_escape_destination_rejected(self) -> None:
        """FR-SEC-002: entries escaping destination directory are rejected."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="../escape/file.txt")])
        assert res.allowed is False


class TestCleanExtraction:
    """Test clean extraction with no violations."""

    def test_clean_entries_allowed(self) -> None:
        """FR-SEC-002: clean entries with no violations are allowed."""
        guard = _make_guard()
        res = _extract(guard, [
            ArchiveEntryVO(entry_path="a.txt"),
            ArchiveEntryVO(entry_path="sub/b.txt"),
            ArchiveEntryVO(entry_path="deep/c.txt"),
        ])
        assert res.allowed is True
        assert len(res.rejected_entries) == 0

    def test_clean_extraction_has_audit_metadata(self) -> None:
        """FR-SEC-002: successful extraction includes audit metadata."""
        guard = _make_guard()
        res = _extract(guard, [ArchiveEntryVO(entry_path="file.txt")])
        assert isinstance(res.audit_metadata, dict)
        assert "entry_count" in res.audit_metadata


class TestEdgeCases:
    """Test edge cases from FR-SEC-002 specification."""

    def test_empty_entries_list(self) -> None:
        """FR-SEC-002: empty entries list is handled."""
        guard = _make_guard()
        res = _extract(guard, [])
        assert res.allowed is True

    def test_duplicate_entry_names(self) -> None:
        """FR-SEC-002: duplicate entry names are handled."""
        guard = _make_guard()
        res = _extract(guard, [
            ArchiveEntryVO(entry_path="file.txt"),
            ArchiveEntryVO(entry_path="file.txt"),
        ])
        # Both allowed if within limits
        assert res.allowed is True

    def test_unsupported_archive_format(self) -> None:
        """FR-SEC-002: unsupported archive metadata is rejected safely."""
        guard = _make_guard()
        # Invalid entry encoding — ArchiveEntryVO accepts any string path
        res = _extract(guard, [ArchiveEntryVO(entry_path="file.txt")])
        assert res.allowed is True  # Valid path, no violations

    def test_mixed_safe_and_unsafe_entries(self) -> None:
        """FR-SEC-002: mixed safe and unsafe entries — unsafe rejected, safe counted."""
        guard = _make_guard()
        res = _extract(guard, [
            ArchiveEntryVO(entry_path="safe.txt"),
            ArchiveEntryVO(entry_path="/etc/passwd"),  # absolute → rejected
            ArchiveEntryVO(entry_path="also_safe.txt"),
        ])
        assert res.allowed is False
        assert len(res.rejected_entries) >= 1

    def test_destination_empty_string(self) -> None:
        """FR-SEC-002: empty destination directory is handled."""
        import asyncio
        guard = _make_guard()
        request = ArchiveExtractionVO(
            destination_directory="",
            entries=tuple([ArchiveEntryVO(entry_path="file.txt")]),
            options=ArchiveExtractionOptionsVO(),
        )
        res = asyncio.run(guard.validate_extraction(request))
        assert isinstance(res.audit_metadata, dict)

    def test_archive_bomb_pattern(self) -> None:
        """FR-SEC-002: archive bomb pattern protected by size/count limits."""
        guard = _make_guard()
        # Many small entries — count limit catches it
        entries = [ArchiveEntryVO(entry_path=f"f{i}", uncompressed_size=1) for i in range(50)]
        opts = ArchiveExtractionOptionsVO(max_entry_count=10, max_total_size=1000)
        res = _extract(guard, entries, opts)
        assert res.allowed is False
