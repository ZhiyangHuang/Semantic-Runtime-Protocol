from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIRST_PAPER_DIR = ROOT / "first_paper"
LATEX_DIR = FIRST_PAPER_DIR / "latex"
RESULTS_DIR = ROOT / "srp_experiment" / "results"
SUBMISSION_DIR = FIRST_PAPER_DIR / "submission"
DEFAULT_REPORT_DIR = SUBMISSION_DIR
DEFAULT_ZIP_PATH = SUBMISSION_DIR / "srp_submission_package.zip"
DEFAULT_COMPILE_LOG_PATH = SUBMISSION_DIR / "main_submission.compile.log"


@dataclass
class CheckResult:
    name: str
    status: str
    details: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _run_command(command: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _copy_if_exists(src: Path, dest: Path) -> bool:
    if not src.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def check_compile(target: str = "submission", dry_run: bool = False, log_path: Path | None = None) -> CheckResult:
    tex = LATEX_DIR / "main_submission.tex"
    pdf = LATEX_DIR / "main_submission.pdf"
    build = LATEX_DIR / "build.ps1"
    details: list[str] = []

    if not tex.exists():
        return CheckResult("compile", "FAIL", [f"Missing source: {_rel(tex)}"])

    if dry_run:
        if pdf.exists():
            details.append(f"PDF present: {_rel(pdf)}")
            return CheckResult("compile", "PASS", details)
        return CheckResult("compile", "FAIL", [f"Missing PDF: {_rel(pdf)}"])

    if shutil.which("powershell") is None and shutil.which("pwsh") is None:
        return CheckResult("compile", "FAIL", ["No PowerShell executable found on PATH."])

    shell = "powershell" if shutil.which("powershell") is not None else "pwsh"
    command = [
        shell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(build),
        "-Clean",
        "-Target",
        target,
    ]
    code, output = _run_command(command, LATEX_DIR)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(output, encoding="utf-8")
    if code != 0:
        tail = "\n".join(output.splitlines()[-40:])
        return CheckResult("compile", "FAIL", [f"Build command failed: {' '.join(command)}", tail or "No output captured."])
    if not pdf.exists():
        return CheckResult("compile", "FAIL", [f"Expected PDF not found after build: {_rel(pdf)}"])
    details.append(f"Build succeeded: {_rel(pdf)}")
    return CheckResult("compile", "PASS", details)


def check_artifact_presence() -> CheckResult:
    required = [
        RESULTS_DIR / "paper_figure_pack" / "main_3panel_figure.png",
        RESULTS_DIR / "paper_figure_pack" / "drift_plot.png",
        RESULTS_DIR / "paper_figure_pack" / "contract_commit_plot.png",
        RESULTS_DIR / "paper_table.tex",
        RESULTS_DIR / "quality_table.tex",
        RESULTS_DIR / "efficiency_table.tex",
        RESULTS_DIR / "guardrail_table.tex",
        RESULTS_DIR / "camera_ready_table.tex",
        RESULTS_DIR / "batch_summary_table.json",
        RESULTS_DIR / "batch_summary_table.csv",
        RESULTS_DIR / "batch_summary_table.md",
        RESULTS_DIR / "evidence_pipeline" / "execution_trace_log.json",
        RESULTS_DIR / "evidence_pipeline" / "execution_trace_table.json",
        RESULTS_DIR / "evidence_pipeline" / "evidence_manifest.json",
    ]
    missing = [f"Missing artifact: {_rel(path)}" for path in required if not path.exists()]
    if missing:
        return CheckResult("artifact_presence", "FAIL", missing)
    return CheckResult("artifact_presence", "PASS", [f"Validated {len(required)} required artifacts."])


def check_reviewer_visible() -> CheckResult:
    tex = LATEX_DIR / "main_submission.tex"
    if not tex.exists():
        return CheckResult("reviewer_visible", "FAIL", [f"Missing source: {_rel(tex)}"])
    text = _read_text(tex)
    expectations = {
        "main figure": "../../srp_experiment/results/paper_figure_pack/main_3panel_figure.png",
        "camera-ready table": "../../srp_experiment/results/camera_ready_table.tex",
    }
    missing = [name for name, needle in expectations.items() if needle not in text]
    details = []
    if missing:
        details.append("Missing reviewer-visible references: " + ", ".join(missing))
        return CheckResult("reviewer_visible", "FAIL", details)
    details.append("Main figure and camera-ready table are referenced in main_submission.tex.")
    return CheckResult("reviewer_visible", "PASS", details)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(_read_text(path))
    except json.JSONDecodeError:
        return None


def check_reproducibility() -> CheckResult:
    details: list[str] = []
    report_paths = [
        RESULTS_DIR / "paper_figure_core_local" / "qualification_report.json",
        RESULTS_DIR / "experiment_qualification_report.json",
    ]
    report = None
    for path in report_paths:
        data = _load_json(path)
        if isinstance(data, dict):
            report = data
            details.append(f"Found qualification report: {_rel(path)}")
            break
    if report is None:
        return CheckResult("reproducibility", "FAIL", [f"Missing qualification report in: {', '.join(_rel(p) for p in report_paths)}"])

    status = str(report.get("status", "")).upper()
    if status != "QUALIFIED":
        return CheckResult("reproducibility", "FAIL", [f"Qualification status is not QUALIFIED: {status or 'missing'}"])
    details.append("Qualification status is QUALIFIED.")

    required_roots = [
        RESULTS_DIR / "paper_figure_core_local",
        RESULTS_DIR / "paper_figure_pack",
        RESULTS_DIR / "evidence_pipeline",
    ]
    missing_roots = [f"Missing evidence root: {_rel(path)}" for path in required_roots if not path.exists()]
    if missing_roots:
        return CheckResult("reproducibility", "FAIL", details + missing_roots)
    details.append("Evidence roots exist for core batch, figure pack, and evidence pipeline.")

    trace_table = RESULTS_DIR / "evidence_pipeline" / "execution_trace_table.json"
    manifest = RESULTS_DIR / "evidence_pipeline" / "evidence_manifest.json"
    if not trace_table.exists() or not manifest.exists():
        return CheckResult(
            "reproducibility",
            "FAIL",
            details + [f"Missing trace or manifest: {_rel(trace_table)}, {_rel(manifest)}"],
        )
    details.append("Trace table and manifest exist.")
    return CheckResult("reproducibility", "PASS", details)


def check_zip_ready(zip_path: Path) -> CheckResult:
    manifest = RESULTS_DIR / "evidence_pipeline" / "evidence_manifest.json"
    if not manifest.exists():
        return CheckResult("zip_ready", "FAIL", [f"Missing manifest: {_rel(manifest)}"])
    if zip_path.exists():
        return CheckResult("zip_ready", "PASS", [f"Zip target ready: {_rel(zip_path)}"])
    return CheckResult("zip_ready", "PASS", [f"Zip target will be created at: {_rel(zip_path)}"])


def generate_zip(zip_path: Path, report_path: Path) -> list[str]:
    include_paths = [
        FIRST_PAPER_DIR / "latex" / "main_submission.tex",
        FIRST_PAPER_DIR / "latex" / "main_submission.pdf",
        FIRST_PAPER_DIR / "latex" / "references.bib",
        FIRST_PAPER_DIR / "latex" / "build.ps1",
        FIRST_PAPER_DIR / "latex" / "README.md",
        FIRST_PAPER_DIR / "latex" / "compile.md",
        RESULTS_DIR / "paper_figure_pack" / "main_3panel_figure.png",
        RESULTS_DIR / "paper_figure_pack" / "drift_plot.png",
        RESULTS_DIR / "paper_figure_pack" / "contract_commit_plot.png",
        RESULTS_DIR / "paper_table.tex",
        RESULTS_DIR / "quality_table.tex",
        RESULTS_DIR / "efficiency_table.tex",
        RESULTS_DIR / "guardrail_table.tex",
        RESULTS_DIR / "camera_ready_table.tex",
        RESULTS_DIR / "batch_summary_table.json",
        RESULTS_DIR / "batch_summary_table.csv",
        RESULTS_DIR / "batch_summary_table.md",
        RESULTS_DIR / "paper_table.md",
        RESULTS_DIR / "quality_table.md",
        RESULTS_DIR / "efficiency_table.md",
        RESULTS_DIR / "guardrail_table.md",
        RESULTS_DIR / "camera_ready_table.md",
        RESULTS_DIR / "evidence_pipeline" / "execution_trace_log.json",
        RESULTS_DIR / "evidence_pipeline" / "execution_trace_table.json",
        RESULTS_DIR / "evidence_pipeline" / "evidence_manifest.json",
        report_path,
    ]
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    added: list[str] = []
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in include_paths:
            if path.exists():
                arcname = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name
                zf.write(path, arcname=str(arcname))
                added.append(str(arcname))
    return added


def build_report(checks: list[CheckResult], zip_path: Path, zip_created: bool) -> dict[str, Any]:
    ready = all(check.passed for check in checks)
    status = "READY_TO_FREEZE" if ready else "NOT_READY"
    return {
        "timestamp": _now_iso(),
        "status": status,
        "zip_path": _rel(zip_path),
        "zip_created": zip_created,
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "details": check.details,
            }
            for check in checks
        ],
    }


def format_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Submission Audit Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Timestamp: `{report['timestamp']}`",
        f"- Zip: `{report['zip_path']}`",
        f"- Zip created: `{report['zip_created']}`",
        "",
        "## Checks",
    ]
    for check in report["checks"]:
        lines.append(f"### {check['name']}")
        lines.append(f"- Status: `{check['status']}`")
        for detail in check["details"]:
            lines.append(f"- {detail}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SRP submission audit.")
    parser.add_argument("--target", default="submission", choices=["submission", "acl", "neurips"], help="LaTeX target to compile.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR), help="Directory for audit reports.")
    parser.add_argument("--zip-path", default=str(DEFAULT_ZIP_PATH), help="Path to the final submission zip.")
    parser.add_argument("--submission-dir", default=str(SUBMISSION_DIR), help="Fixed submission directory that stores the final audit bundle.")
    parser.add_argument("--compile-log-path", default=str(DEFAULT_COMPILE_LOG_PATH), help="Path used to mirror the main compile log into the submission directory.")
    parser.add_argument("--skip-compile", action="store_true", help="Skip the compile check.")
    parser.add_argument("--create-zip", action="store_true", help="Generate the final submission zip if all checks pass.")
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    zip_path = Path(args.zip_path)
    submission_dir = Path(args.submission_dir)
    compile_log_path = Path(args.compile_log_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    submission_dir.mkdir(parents=True, exist_ok=True)

    checks: list[CheckResult] = []
    if args.skip_compile:
        checks.append(CheckResult("compile", "PASS", ["Compile check skipped by request."]))
        compile_log_path.parent.mkdir(parents=True, exist_ok=True)
        compile_log_path.write_text("Compile check skipped by request.\n", encoding="utf-8")
    else:
        checks.append(check_compile(target=args.target, log_path=compile_log_path))
    checks.append(check_artifact_presence())
    checks.append(check_reviewer_visible())
    checks.append(check_reproducibility())
    checks.append(check_zip_ready(zip_path))

    report = build_report(checks, zip_path, zip_created=False)
    report_json = report_dir / "submission_audit_report.json"
    report_md = report_dir / "submission_audit_report.md"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(format_markdown(report), encoding="utf-8")

    zip_created = False
    if report["status"] == "READY_TO_FREEZE" and args.create_zip:
        generate_zip(zip_path, report_json)
        zip_created = True
        report = build_report(checks, zip_path, zip_created=True)
        report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report_md.write_text(format_markdown(report), encoding="utf-8")

    manifest_path = submission_dir / "submission_audit_manifest.json"
    manifest = {
        "timestamp": _now_iso(),
        "status": report["status"],
        "submission_dir": _rel(submission_dir),
        "report_json": _rel(report_json),
        "report_md": _rel(report_md),
        "zip_path": _rel(zip_path),
        "compile_log_path": _rel(compile_log_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(report_md.read_text(encoding="utf-8"))
    return 0 if report["status"] == "READY_TO_FREEZE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
