import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

from env_utils import load_env_file


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DEFAULT_INPUT_JSON = RESULTS_DIR / "batch_summary_table.json"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "paper_table.md"
DEFAULT_OUTPUT_TEX = RESULTS_DIR / "paper_table.tex"
DEFAULT_QUALITY_MD = RESULTS_DIR / "quality_table.md"
DEFAULT_QUALITY_TEX = RESULTS_DIR / "quality_table.tex"
DEFAULT_EFFICIENCY_MD = RESULTS_DIR / "efficiency_table.md"
DEFAULT_EFFICIENCY_TEX = RESULTS_DIR / "efficiency_table.tex"
DEFAULT_TOKEN_BREAKDOWN_MD = RESULTS_DIR / "token_breakdown_table.md"
DEFAULT_TOKEN_BREAKDOWN_TEX = RESULTS_DIR / "token_breakdown_table.tex"
DEFAULT_GUARDRAIL_MD = RESULTS_DIR / "guardrail_table.md"
DEFAULT_GUARDRAIL_TEX = RESULTS_DIR / "guardrail_table.tex"
DEFAULT_CAMERA_READY_MD = RESULTS_DIR / "camera_ready_table.md"
DEFAULT_CAMERA_READY_TEX = RESULTS_DIR / "camera_ready_table.tex"

load_env_file()


def parse_args():
    parser = argparse.ArgumentParser(description="Format batch summaries into compact paper-ready tables.")
    parser.add_argument("--input-json", default=os.getenv("SRP_PAPER_TABLE_INPUT", str(DEFAULT_INPUT_JSON)))
    parser.add_argument("--output-md", default=os.getenv("SRP_PAPER_TABLE_MD", str(DEFAULT_OUTPUT_MD)))
    parser.add_argument("--output-tex", default=os.getenv("SRP_PAPER_TABLE_TEX", str(DEFAULT_OUTPUT_TEX)))
    parser.add_argument("--quality-md", default=os.getenv("SRP_QUALITY_TABLE_MD", str(DEFAULT_QUALITY_MD)))
    parser.add_argument("--quality-tex", default=os.getenv("SRP_QUALITY_TABLE_TEX", str(DEFAULT_QUALITY_TEX)))
    parser.add_argument("--efficiency-md", default=os.getenv("SRP_EFFICIENCY_TABLE_MD", str(DEFAULT_EFFICIENCY_MD)))
    parser.add_argument("--efficiency-tex", default=os.getenv("SRP_EFFICIENCY_TABLE_TEX", str(DEFAULT_EFFICIENCY_TEX)))
    parser.add_argument("--token-breakdown-md", default=os.getenv("SRP_TOKEN_BREAKDOWN_MD", str(DEFAULT_TOKEN_BREAKDOWN_MD)))
    parser.add_argument("--token-breakdown-tex", default=os.getenv("SRP_TOKEN_BREAKDOWN_TEX", str(DEFAULT_TOKEN_BREAKDOWN_TEX)))
    parser.add_argument("--guardrail-md", default=os.getenv("SRP_GUARDRAIL_TABLE_MD", str(DEFAULT_GUARDRAIL_MD)))
    parser.add_argument("--guardrail-tex", default=os.getenv("SRP_GUARDRAIL_TABLE_TEX", str(DEFAULT_GUARDRAIL_TEX)))
    parser.add_argument("--camera-ready-md", default=os.getenv("SRP_CAMERA_READY_MD", str(DEFAULT_CAMERA_READY_MD)))
    parser.add_argument("--camera-ready-tex", default=os.getenv("SRP_CAMERA_READY_TEX", str(DEFAULT_CAMERA_READY_TEX)))
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    repo_relative = ROOT.parent / path
    if repo_relative.exists() or "srp_experiment" in value:
        return repo_relative
    return ROOT / path


def load_rows(path: Path) -> List[Dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def method_sort_key(method: str) -> Tuple[int, str]:
    order = {
        "raw_prompt": 0,
        "summarization": 1,
        "rag": 2,
        "srp": 3,
        "rag_srp": 4,
        "rag_srp_anchor": 5,
        "rag_srp_v2": 6,
    }
    return (order.get(method, 99), method)


def group_rows(rows: List[Dict]) -> Tuple[List[str], List[Dict]]:
    methods = sorted({row["method"] for row in rows}, key=method_sort_key)
    grouped: Dict[Tuple[str, str, int], Dict] = {}
    for row in rows:
        key = (row["backend"], row["model"], int(row["cycles"]))
        entry = grouped.setdefault(
            key,
            {
                "backend": row["backend"],
                "model": row["model"],
                "cycles": int(row["cycles"]),
                "metrics": {},
            },
        )
        entry["metrics"][row["method"]] = {
            "drift": float(row["mean_drift"]),
            "success": float(row["mean_task_success"]),
            "tokens": float(row["mean_tokens"]),
            "latency": float(row["mean_latency_seconds"]) if row.get("mean_latency_seconds") not in ("", None) else None,
            "prompt_tokens": float(row["mean_prompt_tokens"]) if row.get("mean_prompt_tokens") not in ("", None) else None,
            "completion_tokens": float(row["mean_completion_tokens"]) if row.get("mean_completion_tokens") not in ("", None) else None,
            "total_tokens": float(row["mean_total_tokens"]) if row.get("mean_total_tokens") not in ("", None) else None,
            "query_prompt_tokens": float(row["mean_query_prompt_tokens"]) if row.get("mean_query_prompt_tokens") not in ("", None) else None,
            "query_completion_tokens": float(row["mean_query_completion_tokens"]) if row.get("mean_query_completion_tokens") not in ("", None) else None,
            "query_total_tokens": float(row["mean_query_total_tokens"]) if row.get("mean_query_total_tokens") not in ("", None) else None,
            "judge_prompt_tokens": float(row["mean_judge_prompt_tokens"]) if row.get("mean_judge_prompt_tokens") not in ("", None) else None,
            "judge_completion_tokens": float(row["mean_judge_completion_tokens"]) if row.get("mean_judge_completion_tokens") not in ("", None) else None,
            "judge_total_tokens": float(row["mean_judge_total_tokens"]) if row.get("mean_judge_total_tokens") not in ("", None) else None,
            "commit_rate": float(row["commit_rate"]) if row.get("commit_rate") not in ("", None) else None,
            "validation_drift": float(row["mean_validation_drift"]) if row.get("mean_validation_drift") not in ("", None) else None,
            "rollback_count": int(row["rollback_count"]) if row.get("rollback_count") not in ("", None) else None,
        }
    grouped_rows = sorted(grouped.values(), key=lambda item: (item["backend"], item["model"], item["cycles"]))
    return methods, grouped_rows


def fmt_metric(value, digits: int = 3) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def compute_best_metrics(methods: List[str], row: Dict) -> Dict[str, float]:
    best = {"drift": None, "success": None, "tokens": None, "latency": None}
    for method in methods:
        metrics = row["metrics"].get(method)
        if not metrics:
            continue
        drift = metrics.get("drift")
        success = metrics.get("success")
        tokens = metrics.get("tokens")
        latency = metrics.get("latency")
        if drift is not None and (best["drift"] is None or drift < best["drift"]):
            best["drift"] = drift
        if success is not None and (best["success"] is None or success > best["success"]):
            best["success"] = success
        if tokens is not None and (best["tokens"] is None or tokens < best["tokens"]):
            best["tokens"] = tokens
        if latency is not None and (best["latency"] is None or latency < best["latency"]):
            best["latency"] = latency
    return best


def select_strongest_baseline(row: Dict) -> Tuple[str, Dict]:
    candidates = []
    for method, metrics in row["metrics"].items():
        if method == "srp":
            continue
        candidates.append((method, metrics))
    if not candidates:
        return "", {}
    candidates.sort(
        key=lambda item: (
            -item[1].get("success", float("-inf")),
            item[1].get("drift", float("inf")),
            item[1].get("tokens", float("inf")),
            method_sort_key(item[0]),
        )
    )
    return candidates[0]


def write_markdown(path: Path, methods: List[str], grouped_rows: List[Dict]):
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = method.replace("_", " ").title()
        headers.extend([f"{label} Drift", f"{label} Success", f"{label} Tokens", f"{label} Latency (s)"])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in grouped_rows:
        values = [row["backend"], row["model"], str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("drift")),
                    fmt_metric(metrics.get("success")),
                    fmt_metric(metrics.get("tokens"), digits=2),
                    fmt_metric(metrics.get("latency"), digits=4),
                ]
            )
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quality_markdown(path: Path, methods: List[str], grouped_rows: List[Dict]):
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = method.replace("_", " ").title()
        headers.extend([f"{label} Drift", f"{label} Success"])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in grouped_rows:
        values = [row["backend"], row["model"], str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("drift")),
                    fmt_metric(metrics.get("success")),
                ]
            )
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_efficiency_markdown(path: Path, methods: List[str], grouped_rows: List[Dict]):
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = method.replace("_", " ").title()
        headers.extend(
            [
                f"{label} Tokens",
                f"{label} Latency (s)",
                f"{label} Prompt Tok",
                f"{label} Completion Tok",
                f"{label} Total Tok",
            ]
        )
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in grouped_rows:
        values = [row["backend"], row["model"], str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("tokens"), digits=2),
                    fmt_metric(metrics.get("latency"), digits=4),
                    fmt_metric(metrics.get("prompt_tokens"), digits=2),
                    fmt_metric(metrics.get("completion_tokens"), digits=2),
                    fmt_metric(metrics.get("total_tokens"), digits=2),
                ]
            )
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_token_breakdown_markdown(path: Path, methods: List[str], grouped_rows: List[Dict]):
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = method.replace("_", " ").title()
        headers.extend(
            [
                f"{label} Query Prompt",
                f"{label} Query Completion",
                f"{label} Query Total",
                f"{label} Judge Prompt",
                f"{label} Judge Completion",
                f"{label} Judge Total",
            ]
        )
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in grouped_rows:
        values = [row["backend"], row["model"], str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("query_prompt_tokens"), digits=2),
                    fmt_metric(metrics.get("query_completion_tokens"), digits=2),
                    fmt_metric(metrics.get("query_total_tokens"), digits=2),
                    fmt_metric(metrics.get("judge_prompt_tokens"), digits=2),
                    fmt_metric(metrics.get("judge_completion_tokens"), digits=2),
                    fmt_metric(metrics.get("judge_total_tokens"), digits=2),
                ]
            )
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_token_breakdown_latex(path: Path, methods: List[str], grouped_rows: List[Dict]):
    column_spec = "lll" + "rrrrrr" * len(methods)
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = short_method_label(method)
        headers.extend(
            [
                f"{label} QP",
                f"{label} QC",
                f"{label} QT",
                f"{label} JP",
                f"{label} JC",
                f"{label} JT",
            ]
        )
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\scriptsize",
        f"\\begin{{tabular}}{{{column_spec}}}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in grouped_rows:
        values = [escape_latex(row["backend"]), escape_latex(row["model"]), str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("query_prompt_tokens"), digits=2),
                    fmt_metric(metrics.get("query_completion_tokens"), digits=2),
                    fmt_metric(metrics.get("query_total_tokens"), digits=2),
                    fmt_metric(metrics.get("judge_prompt_tokens"), digits=2),
                    fmt_metric(metrics.get("judge_completion_tokens"), digits=2),
                    fmt_metric(metrics.get("judge_total_tokens"), digits=2),
                ]
            )
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Token breakdown table. QP = query prompt tokens, QC = query completion tokens, QT = query total tokens, JP = judge prompt tokens, JC = judge completion tokens, JT = judge total tokens.}",
            "\\label{tab:srp-token-breakdown}",
            "\\end{table*}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_markdown(path: Path, methods: List[str], grouped_rows: List[Dict]):
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = method.replace("_", " ").title()
        headers.extend([f"{label} Commit Rate", f"{label} Validation Drift", f"{label} Rollbacks"])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in grouped_rows:
        values = [row["backend"], row["model"], str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("commit_rate"), digits=4),
                    fmt_metric(metrics.get("validation_drift"), digits=4),
                    str(metrics.get("rollback_count")) if metrics.get("rollback_count") is not None else "-",
                ]
            )
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_camera_ready_markdown(path: Path, grouped_rows: List[Dict]):
    lines = [
        "| Backend | Model | Cycles | Strongest Baseline | Baseline Drift | Baseline Success | Baseline Tokens | Baseline Latency (s) | SRP Drift | SRP Success | SRP Tokens | SRP Latency (s) | Delta Drift | Delta Success | Delta Tokens | Delta Latency (s) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in grouped_rows:
        baseline_name, baseline_metrics = select_strongest_baseline(row)
        srp_metrics = row["metrics"].get("srp", {})
        base_drift = baseline_metrics.get("drift")
        base_success = baseline_metrics.get("success")
        base_tokens = baseline_metrics.get("tokens")
        base_latency = baseline_metrics.get("latency")
        srp_drift = srp_metrics.get("drift")
        srp_success = srp_metrics.get("success")
        srp_tokens = srp_metrics.get("tokens")
        srp_latency = srp_metrics.get("latency")
        delta_drift = srp_drift - base_drift if srp_drift is not None and base_drift is not None else None
        delta_success = srp_success - base_success if srp_success is not None and base_success is not None else None
        delta_tokens = srp_tokens - base_tokens if srp_tokens is not None and base_tokens is not None else None
        delta_latency = srp_latency - base_latency if srp_latency is not None and base_latency is not None else None
        lines.append(
            "| "
            + " | ".join(
                [
                    row["backend"],
                    row["model"],
                    str(row["cycles"]),
                    baseline_name.replace("_", " ").title() if baseline_name else "-",
                    fmt_metric(base_drift),
                    fmt_metric(base_success),
                    fmt_metric(base_tokens, digits=2),
                    fmt_metric(base_latency, digits=4),
                    fmt_metric(srp_drift),
                    fmt_metric(srp_success),
                    fmt_metric(srp_tokens, digits=2),
                    fmt_metric(srp_latency, digits=4),
                    fmt_metric(delta_drift),
                    fmt_metric(delta_success),
                    fmt_metric(delta_tokens, digits=2),
                    fmt_metric(delta_latency, digits=4),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def escape_latex(text: str) -> str:
    return text.replace("_", "\\_")


def short_method_label(method: str) -> str:
    mapping = {
        "raw_prompt": "RP",
        "summarization": "Sum",
        "rag": "RAG",
        "srp": "SRP",
        "rag_srp": "R+S",
        "rag_srp_anchor": "R+SA",
        "rag_srp_v2": "R+S2",
    }
    return mapping.get(method, method.upper())


def write_latex(path: Path, methods: List[str], grouped_rows: List[Dict]):
    column_spec = "lll" + "rrrr" * len(methods)
    headers = ["Backend", "Model", "Cycles"]
    for method in methods:
        label = method.replace("_", " ").title()
        headers.extend([f"{label} D", f"{label} S", f"{label} T", f"{label} L"])

    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        f"\\begin{{tabular}}{{{column_spec}}}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in grouped_rows:
        best = compute_best_metrics(methods, row)
        values = [escape_latex(row["backend"]), escape_latex(row["model"]), str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            drift_value = metrics.get("drift")
            success_value = metrics.get("success")
            tokens_value = metrics.get("tokens")
            latency_value = metrics.get("latency")
            drift_text = fmt_metric(drift_value)
            success_text = fmt_metric(success_value)
            tokens_text = fmt_metric(tokens_value, digits=2)
            latency_text = fmt_metric(latency_value, digits=4)
            if drift_value is not None and best["drift"] is not None and abs(drift_value - best["drift"]) < 1e-12:
                drift_text = f"\\textbf{{{drift_text}}}"
            if success_value is not None and best["success"] is not None and abs(success_value - best["success"]) < 1e-12:
                success_text = f"\\textbf{{{success_text}}}"
            if tokens_value is not None and best["tokens"] is not None and abs(tokens_value - best["tokens"]) < 1e-12:
                tokens_text = f"\\textbf{{{tokens_text}}}"
            if latency_value is not None and best["latency"] is not None and abs(latency_value - best["latency"]) < 1e-12:
                latency_text = f"\\textbf{{{latency_text}}}"
            values.extend(
                [
                    drift_text,
                    success_text,
                    tokens_text,
                    latency_text,
                ]
            )
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Compact comparison table across backends, models, cycle counts, and methods. Bold indicates the best value in each row for each metric group. D = mean drift, S = mean task success, T = mean tokens, L = mean latency in seconds.}",
            "\\label{tab:srp-paper-table}",
            "\\end{table*}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quality_latex(path: Path, methods: List[str], grouped_rows: List[Dict]):
    column_spec = "llr" + "rr" * len(methods)
    headers = ["B", "M", "C"]
    for method in methods:
        label = short_method_label(method)
        headers.extend([f"{label} D", f"{label} S"])

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\scriptsize",
        f"\\begin{{tabular}}{{{column_spec}}}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in grouped_rows:
        best = compute_best_metrics(methods, row)
        values = [escape_latex(row["backend"]), escape_latex(row["model"]), str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            drift_value = metrics.get("drift")
            success_value = metrics.get("success")
            drift_text = fmt_metric(drift_value)
            success_text = fmt_metric(success_value)
            if drift_value is not None and best["drift"] is not None and abs(drift_value - best["drift"]) < 1e-12:
                drift_text = f"\\textbf{{{drift_text}}}"
            if success_value is not None and best["success"] is not None and abs(success_value - best["success"]) < 1e-12:
                success_text = f"\\textbf{{{success_text}}}"
            values.extend([drift_text, success_text])
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Quality comparison. B = backend, M = model, C = cycles, RP = raw prompt, Sum = summarization, RAG = retrieval-augmented generation, SRP = Semantic Runtime Protocol. Bold indicates the best value in each row. Lower drift is better; higher success is better.}",
            "\\label{tab:srp-quality-table}",
            "\\end{table}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_efficiency_latex(path: Path, methods: List[str], grouped_rows: List[Dict]):
    column_spec = "llr" + "rr" * len(methods)
    headers = ["B", "M", "C"]
    for method in methods:
        label = short_method_label(method)
        headers.extend([f"{label} T", f"{label} L"])

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\scriptsize",
        f"\\begin{{tabular}}{{{column_spec}}}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in grouped_rows:
        best = compute_best_metrics(methods, row)
        values = [escape_latex(row["backend"]), escape_latex(row["model"]), str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            tokens_value = metrics.get("tokens")
            latency_value = metrics.get("latency")
            tokens_text = fmt_metric(tokens_value, digits=2)
            latency_text = fmt_metric(latency_value, digits=4)
            if tokens_value is not None and best["tokens"] is not None and abs(tokens_value - best["tokens"]) < 1e-12:
                tokens_text = f"\\textbf{{{tokens_text}}}"
            if latency_value is not None and best["latency"] is not None and abs(latency_value - best["latency"]) < 1e-12:
                latency_text = f"\\textbf{{{latency_text}}}"
            values.extend([tokens_text, latency_text])
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Efficiency comparison. B = backend, M = model, C = cycles, RP = raw prompt, Sum = summarization, RAG = retrieval-augmented generation, SRP = Semantic Runtime Protocol. T = mean tokens and L = mean latency in seconds. Bold indicates the lowest value in each row for each efficiency metric.}",
            "\\label{tab:srp-efficiency-table}",
            "\\end{table}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_latex(path: Path, methods: List[str], grouped_rows: List[Dict]):
    column_spec = "llr" + "rrr" * len(methods)
    headers = ["B", "M", "C"]
    for method in methods:
        label = short_method_label(method)
        headers.extend([f"{label} CR", f"{label} VD", f"{label} RB"])

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\scriptsize",
        f"\\begin{{tabular}}{{{column_spec}}}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in grouped_rows:
        values = [escape_latex(row["backend"]), escape_latex(row["model"]), str(row["cycles"])]
        for method in methods:
            metrics = row["metrics"].get(method, {})
            values.extend(
                [
                    fmt_metric(metrics.get("commit_rate"), digits=4),
                    fmt_metric(metrics.get("validation_drift"), digits=4),
                    str(metrics.get("rollback_count")) if metrics.get("rollback_count") is not None else "-",
                ]
            )
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Guardrail diagnostics. CR = commit rate, VD = mean validation drift, and RB = rollback count. Dashes indicate methods that do not implement SRP-style commit and rollback semantics.}",
            "\\label{tab:srp-guardrail-table}",
            "\\end{table}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_camera_ready_latex(path: Path, grouped_rows: List[Dict]):
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\setlength{\\tabcolsep}{2pt}",
        "\\scriptsize",
        "\\begin{tabular}{llrlrrrrrrrrrrrr}",
        "\\toprule",
        "B & M & C & Base & Base D & Base S & Base T & Base L & SRP D & SRP S & SRP T & SRP L & $\\Delta$D & $\\Delta$S & $\\Delta$T & $\\Delta$L \\\\",
        "\\midrule",
    ]
    for row in grouped_rows:
        baseline_name, baseline_metrics = select_strongest_baseline(row)
        srp_metrics = row["metrics"].get("srp", {})
        base_drift = baseline_metrics.get("drift")
        base_success = baseline_metrics.get("success")
        base_tokens = baseline_metrics.get("tokens")
        base_latency = baseline_metrics.get("latency")
        srp_drift = srp_metrics.get("drift")
        srp_success = srp_metrics.get("success")
        srp_tokens = srp_metrics.get("tokens")
        srp_latency = srp_metrics.get("latency")
        delta_drift = srp_drift - base_drift if srp_drift is not None and base_drift is not None else None
        delta_success = srp_success - base_success if srp_success is not None and base_success is not None else None
        delta_tokens = srp_tokens - base_tokens if srp_tokens is not None and base_tokens is not None else None
        delta_latency = srp_latency - base_latency if srp_latency is not None and base_latency is not None else None

        base_drift_text = fmt_metric(base_drift)
        base_success_text = fmt_metric(base_success)
        base_tokens_text = fmt_metric(base_tokens, digits=2)
        base_latency_text = fmt_metric(base_latency, digits=4)
        srp_drift_text = fmt_metric(srp_drift)
        srp_success_text = fmt_metric(srp_success)
        srp_tokens_text = fmt_metric(srp_tokens, digits=2)
        srp_latency_text = fmt_metric(srp_latency, digits=4)
        delta_drift_text = fmt_metric(delta_drift)
        delta_success_text = fmt_metric(delta_success)
        delta_tokens_text = fmt_metric(delta_tokens, digits=2)
        delta_latency_text = fmt_metric(delta_latency, digits=4)

        if srp_drift is not None and base_drift is not None and srp_drift < base_drift:
            srp_drift_text = f"\\textbf{{{srp_drift_text}}}"
        elif base_drift is not None and srp_drift is not None and base_drift < srp_drift:
            base_drift_text = f"\\textbf{{{base_drift_text}}}"

        if srp_success is not None and base_success is not None and srp_success > base_success:
            srp_success_text = f"\\textbf{{{srp_success_text}}}"
        elif base_success is not None and srp_success is not None and base_success > srp_success:
            base_success_text = f"\\textbf{{{base_success_text}}}"

        if srp_tokens is not None and base_tokens is not None and srp_tokens < base_tokens:
            srp_tokens_text = f"\\textbf{{{srp_tokens_text}}}"
        elif base_tokens is not None and srp_tokens is not None and base_tokens < srp_tokens:
            base_tokens_text = f"\\textbf{{{base_tokens_text}}}"
        if srp_latency is not None and base_latency is not None and srp_latency < base_latency:
            srp_latency_text = f"\\textbf{{{srp_latency_text}}}"
        elif base_latency is not None and srp_latency is not None and base_latency < srp_latency:
            base_latency_text = f"\\textbf{{{base_latency_text}}}"

        baseline_label = short_method_label(baseline_name) if baseline_name else "-"
        lines.append(
            " & ".join(
                [
                    escape_latex(row["backend"]),
                    escape_latex(row["model"]),
                    str(row["cycles"]),
                    baseline_label,
                    base_drift_text,
                    base_success_text,
                    base_tokens_text,
                    base_latency_text,
                    srp_drift_text,
                    srp_success_text,
                    srp_tokens_text,
                    srp_latency_text,
                    delta_drift_text,
                    delta_success_text,
                    delta_tokens_text,
                    delta_latency_text,
                ]
            )
            + " \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Comparison between Semantic Runtime Protocol (SRP) and the strongest non-SRP baseline for each backend, model, and cycle setting. The baseline is selected by task success, then semantic drift, then token cost. $\\Delta$ denotes SRP minus the selected baseline. Lower drift, token cost, and latency are better, while higher task success is better. Bold indicates the stronger value within each SRP-baseline pair.}",
            "\\label{tab:srp-camera-ready-table}",
            "\\end{table}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    input_json = resolve_path(args.input_json)
    output_md = resolve_path(args.output_md)
    output_tex = resolve_path(args.output_tex)
    quality_md = resolve_path(args.quality_md)
    quality_tex = resolve_path(args.quality_tex)
    efficiency_md = resolve_path(args.efficiency_md)
    efficiency_tex = resolve_path(args.efficiency_tex)
    token_breakdown_md = resolve_path(args.token_breakdown_md)
    token_breakdown_tex = resolve_path(args.token_breakdown_tex)
    guardrail_md = resolve_path(args.guardrail_md)
    guardrail_tex = resolve_path(args.guardrail_tex)
    camera_ready_md = resolve_path(args.camera_ready_md)
    camera_ready_tex = resolve_path(args.camera_ready_tex)

    rows = load_rows(input_json)
    methods, grouped_rows = group_rows(rows)
    write_markdown(output_md, methods, grouped_rows)
    write_latex(output_tex, methods, grouped_rows)
    write_quality_markdown(quality_md, methods, grouped_rows)
    write_quality_latex(quality_tex, methods, grouped_rows)
    write_efficiency_markdown(efficiency_md, methods, grouped_rows)
    write_efficiency_latex(efficiency_tex, methods, grouped_rows)
    write_token_breakdown_markdown(token_breakdown_md, methods, grouped_rows)
    write_token_breakdown_latex(token_breakdown_tex, methods, grouped_rows)
    write_guardrail_markdown(guardrail_md, methods, grouped_rows)
    write_guardrail_latex(guardrail_tex, methods, grouped_rows)
    write_camera_ready_markdown(camera_ready_md, grouped_rows)
    write_camera_ready_latex(camera_ready_tex, grouped_rows)

    print(f"[Format] Input: {input_json}")
    print(f"[Format] Grouped rows: {len(grouped_rows)}")
    print(f"[Format] Markdown: {output_md}")
    print(f"[Format] LaTeX: {output_tex}")
    print(f"[Format] Quality Markdown: {quality_md}")
    print(f"[Format] Quality LaTeX: {quality_tex}")
    print(f"[Format] Efficiency Markdown: {efficiency_md}")
    print(f"[Format] Efficiency LaTeX: {efficiency_tex}")
    print(f"[Format] Token Breakdown Markdown: {token_breakdown_md}")
    print(f"[Format] Token Breakdown LaTeX: {token_breakdown_tex}")
    print(f"[Format] Guardrail Markdown: {guardrail_md}")
    print(f"[Format] Guardrail LaTeX: {guardrail_tex}")
    print(f"[Format] Camera-ready Markdown: {camera_ready_md}")
    print(f"[Format] Camera-ready LaTeX: {camera_ready_tex}")


if __name__ == "__main__":
    main()
