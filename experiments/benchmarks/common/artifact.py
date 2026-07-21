from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .report import render_benchmark_report
from .schema import BenchmarkRunBundle


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_payload(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_benchmark_artifact(output_dir: str | Path, bundle: BenchmarkRunBundle) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    config_path = output_path / "config.json"
    raw_predictions_path = output_path / "raw_predictions.jsonl"
    metrics_path = output_path / "metrics.json"
    report_path = output_path / "report.md"
    metadata_path = output_path / "metadata.json"

    config_path.write_text(json.dumps(bundle.config.as_dict(), ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    with raw_predictions_path.open("w", encoding="utf-8") as handle:
        for prediction in bundle.predictions:
            handle.write(_canonical_json(prediction.as_dict()))
            handle.write("\n")

    metrics_path.write_text(json.dumps(bundle.metrics, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    report_markdown = bundle.report_markdown or render_benchmark_report(bundle)
    report_path.write_text(report_markdown, encoding="utf-8")

    metadata = dict(bundle.metadata)
    metadata["artifact_hashes"] = {
        "config_json": _hash_file(config_path),
        "raw_predictions_jsonl": _hash_file(raw_predictions_path),
        "metrics_json": _hash_file(metrics_path),
        "report_md": _hash_file(report_path),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "config_json": str(config_path),
        "raw_predictions_jsonl": str(raw_predictions_path),
        "metrics_json": str(metrics_path),
        "report_md": str(report_path),
        "metadata_json": str(metadata_path),
    }
