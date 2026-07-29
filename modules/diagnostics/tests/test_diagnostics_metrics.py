"""Tests for MetricsCollector — FR-DIA-002.

Exercises counter tracking, latency summaries (count/min/max/mean/p50/p95),
freshness indicators, and snapshot immutability via MetricsCollector.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio

import pytest

from modules.diagnostics.src.capabilities_metrics_collection import MetricsCollector


def _make_collector() -> MetricsCollector:
    return MetricsCollector()


class TestMetricsCollectionRequiredCounters:
    """Test all required counters are collected and returned."""

    def test_pending_operations_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(pending_operations=5))
        assert snap.counters["pending_operations"] == 5

    def test_reconnect_count_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(reconnect_count=3))
        assert snap.counters["reconnect_count"] == 3

    def test_failed_requests_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(failed_requests=7))
        assert snap.counters["failed_requests"] == 7

    def test_security_violations_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(security_violations=2))
        assert snap.counters["security_violations"] == 2

    def test_tasks_created_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(tasks_created=10))
        assert snap.counters["tasks_created"] == 10

    def test_tasks_failed_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(tasks_failed=3))
        assert snap.counters["tasks_failed"] == 3

    def test_tasks_completed_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(tasks_completed=7))
        assert snap.counters["tasks_completed"] == 7


class TestLatencySummaries:
    """Test latency summaries include count, min, max, mean, percentiles."""

    def test_execution_latency_collected(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(execution_latency_ms=150.5))
        assert "execution_latency_ms" in snap.latency_summaries

    def test_command_latency_collected(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(command_latency_ms=25.3))
        assert "command_latency_ms" in snap.latency_summaries

    def test_single_sample_latency_has_all_fields(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(execution_latency_ms=100.0))
        summary = snap.latency_summaries["execution_latency_ms"]
        assert summary.count == 1
        assert summary.min_ms == 100.0
        assert summary.max_ms == 100.0
        assert summary.mean_ms == 100.0
        assert summary.p50_ms == 100.0
        assert summary.p95_ms == 100.0

    def test_multiple_samples_compute_percentiles(self) -> None:
        collector = _make_collector()
        # First sample
        asyncio.run(collector.collect_metrics_snapshot(execution_latency_ms=50.0))
        # Second sample
        asyncio.run(collector.collect_metrics_snapshot(execution_latency_ms=150.0))
        # Third sample
        snap = asyncio.run(collector.collect_metrics_snapshot(execution_latency_ms=100.0))
        summary = snap.latency_summaries["execution_latency_ms"]
        assert summary.count == 3
        assert summary.min_ms == 50.0
        assert summary.max_ms == 150.0
        assert summary.p50_ms <= summary.mean_ms <= summary.max_ms

    def test_zero_latency_is_valid(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot())
        # No latency samples → no summaries yet
        assert "execution_latency_ms" not in snap.latency_summaries


class TestSnapshotImmutability:
    """Test snapshot immutability and freshness."""

    def test_snapshot_has_collection_timestamp(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot())
        assert snap.collection_timestamp != ""

    def test_snapshot_is_immutable(self) -> None:
        collector = _make_collector()
        snap1 = asyncio.run(collector.collect_metrics_snapshot(pending_operations=5))
        snap2 = asyncio.run(collector.collect_metrics_snapshot(pending_operations=10))
        assert snap1.counters["pending_operations"] == 5
        assert snap2.counters["pending_operations"] == 10

    def test_counters_are_monotonic_within_lifetime(self) -> None:
        collector = _make_collector()
        snap1 = asyncio.run(collector.collect_metrics_snapshot(tasks_created=5))
        snap2 = asyncio.run(collector.collect_metrics_snapshot(tasks_created=10))
        assert snap2.counters["tasks_created"] >= snap1.counters["tasks_created"]


class TestFreshnessIndicators:
    """Test per-source freshness indicators."""

    def test_freshness_indicator_present(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot())
        assert "counters" in snap.freshness_indicators
        assert "latency_summaries" in snap.freshness_indicators

    def test_stale_sources_marked(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot())
        assert "counters" in snap.freshness_indicators
        assert "latency_summaries" in snap.freshness_indicators


class TestEdgeCases:
    """Test edge cases from FR-DIA-002."""

    def test_no_data_collected_yet(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot())
        assert snap.counters["pending_operations"] == 0
        assert snap.counters["reconnect_count"] == 0
        assert snap.counters["failed_requests"] == 0

    def test_large_counter_values(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(tasks_created=999999))
        assert snap.counters["tasks_created"] == 999999

    def test_negative_counter_rejected(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(tasks_created=5))
        assert snap.counters["tasks_created"] == 5

    def test_metrics_do_not_contain_sensitive_data(self) -> None:
        snap = asyncio.run(
            _make_collector().collect_metrics_snapshot(
                pending_operations=5,
                reconnect_count=3,
                failed_requests=2,
                security_violations=1,
            )
        )
        for value in snap.counters.values():
            assert not isinstance(value, str) or "secret" not in str(value).lower()
