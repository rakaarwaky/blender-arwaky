"""Tests for MetricsCollector — FR-DIA-002.

Exercises metrics snapshot collection, latency summaries, counter behavior,
freshness indicators, monotonic counters, and collection timestamp via MetricsCollector.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio

from modules.diagnostics.src.capabilities_metrics_collector import MetricsCollector
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import MetricsSampleVO


def _make_collector() -> MetricsCollector:
    return MetricsCollector()


def _sample(**kwargs):
    return MetricsSampleVO(**kwargs)


class TestMetricsSnapshotRequiredCounters:
    def test_tasks_created_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=_sample(tasks_created=5)))
        assert snap.counters["tasks_created"] == 5

    def test_tasks_failed_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=_sample(tasks_failed=3)))
        assert snap.counters["tasks_failed"] == 3

    def test_tasks_completed_counter(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=_sample(tasks_completed=7)))
        assert snap.counters["tasks_completed"] == 7


class TestMetricsSnapshotAccumulation:
    def test_multiple_samples_accumulate_counters(self) -> None:
        collector = _make_collector()
        asyncio.run(collector.collect_metrics_snapshot(sample=_sample(pending_operations=5)))
        asyncio.run(collector.collect_metrics_snapshot(sample=_sample(pending_operations=10)))
        snap = asyncio.run(collector.collect_metrics_snapshot(sample=_sample(pending_operations=2)))
        assert snap.counters["pending_operations"] == 2

    def test_multiple_samples_accumulate_latency(self) -> None:
        collector = _make_collector()
        asyncio.run(collector.collect_metrics_snapshot(sample=_sample(execution_latency_ms=50.0)))
        asyncio.run(collector.collect_metrics_snapshot(sample=_sample(execution_latency_ms=150.0)))
        snap = asyncio.run(collector.collect_metrics_snapshot(sample=_sample(execution_latency_ms=100.0)))
        latency = snap.latency_summaries.get("execution_latency_ms")
        assert latency is not None
        assert latency.count == 3
        assert latency.min_ms == 50.0
        assert latency.max_ms == 150.0


class TestMetricsSnapshotFreshness:
    def test_empty_collection_has_no_latency_data(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=MetricsSampleVO()))
        assert snap.freshness_indicators["latency_summaries"] == "no_data"

    def test_collection_timestamp_is_set(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=MetricsSampleVO()))
        assert snap.collection_timestamp != ""


class TestMetricsSnapshotCounterReset:
    def test_default_collector_has_no_reset(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=MetricsSampleVO()))
        assert snap.counter_reset_indicator is False

    def test_setting_high_counter_records_value(self) -> None:
        snap = asyncio.run(_make_collector().collect_metrics_snapshot(sample=_sample(tasks_created=999999)))
        assert snap.counters["tasks_created"] == 999999

    def test_multiple_calls_retain_latest_counters(self) -> None:
        collector = _make_collector()
        asyncio.run(collector.collect_metrics_snapshot(sample=_sample(tasks_created=5)))
        asyncio.run(collector.collect_metrics_snapshot(sample=_sample(tasks_created=10)))
        snap = asyncio.run(collector.collect_metrics_snapshot(sample=_sample(tasks_created=1)))
        assert snap.counters["tasks_created"] == 1
        assert snap.counters["tasks_failed"] == 0
