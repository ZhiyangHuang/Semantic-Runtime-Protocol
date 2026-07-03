from __future__ import annotations

import json
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from env_utils import load_env_file


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
GENERATED_DIR = ROOT / "configs" / "generated"
ENV_PATH = ROOT / ".env"

load_env_file()

METHODS = [
    "raw_prompt",
    "summarization",
    "rag",
    "srp",
    "rag_srp_v2",
]

GROUPS = {
    "group_1 (1-100)": "srp_experiment/data/longbench_v2/tasks_group_1.json",
    "group_2 (101-200)": "srp_experiment/data/longbench_v2/tasks_group_2.json",
    "group_3 (201-300)": "srp_experiment/data/longbench_v2/tasks_group_3.json",
}

PROFILES = {
    "Smoke: 100 cycles x 1 repeat": {
        "cycles": [100],
        "repeats": 1,
        "output_root_base": "srp_experiment/results/batch_runs/longbench_launcher_smoke",
    },
    "Formal: 100+1000 cycles x 1 repeat": {
        "cycles": [100, 1000],
        "repeats": 1,
        "output_root_base": "srp_experiment/results/batch_runs/longbench_launcher_formal_single",
    },
    "Formal: 100+1000 cycles x 20 repeats": {
        "cycles": [100, 1000],
        "repeats": 20,
        "output_root_base": "srp_experiment/results/batch_runs/longbench_launcher_formal",
    },
}

PROFILE_DEFAULTS = {item["output_root_base"] for item in PROFILES.values()}

MODEL_CONTEXT_BUDGETS = {
    "qwen/qwen3-4b-awq": 1024,
}

DEFAULT_MODEL = os.getenv("SRP_MODEL", "Qwen/Qwen3-4B-AWQ")
DEFAULT_BACKEND = os.getenv("SRP_BACKEND", "local")


def get_context_budget(model_name: str) -> int | None:
    configured = os.getenv("SRP_MODEL_CONTEXT_BUDGET", "").strip()
    if configured:
        try:
            value = int(configured)
        except ValueError:
            value = 0
        if value > 0:
            return value
    return MODEL_CONTEXT_BUDGETS.get(model_name.lower())


def slugify(value: str) -> str:
    cleaned = []
    for char in value:
        if char.isalnum():
            cleaned.append(char.lower())
        elif char in {"-", "_"}:
            cleaned.append(char)
        else:
            cleaned.append("_")
    return "".join(cleaned).strip("_")


def update_env_value(key: str, value: str) -> None:
    if not ENV_PATH.exists():
        raise FileNotFoundError(f"Missing env file: {ENV_PATH}")
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    updated = False
    new_lines: list[str] = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ[key] = value


def estimate_prompt_risk(method: str, task_file: str, model_name: str) -> dict | None:
    budget = get_context_budget(model_name)
    if budget is None:
        return None

    task_path = REPO_ROOT / task_file
    payload = json.loads(task_path.read_text(encoding="utf-8"))
    tasks = payload.get("tasks", []) if isinstance(payload, dict) else payload
    if not isinstance(tasks, list) or not tasks:
        return None

    memory_lengths = [len(task.get("initial_state", {}).get("memory", "")) for task in tasks]
    query_lengths = [len((task.get("queries") or [""])[0]) for task in tasks]
    max_memory_chars = max(memory_lengths) if memory_lengths else 0
    mean_memory_chars = int(sum(memory_lengths) / len(memory_lengths)) if memory_lengths else 0
    max_query_chars = max(query_lengths) if query_lengths else 0

    risk_level = "LOW"
    reason = ""

    if method == "raw_prompt":
        if max_memory_chars > 100000:
            risk_level = "HIGH"
            reason = "raw_prompt will send very large benchmark memory directly into the model context"
    elif method in {"rag", "rag_srp_v2"}:
        if max_memory_chars > 500000:
            risk_level = "MEDIUM"
            reason = "retrieval-guided methods may still surface large long-context payloads"
    elif method == "summarization":
        if max_memory_chars > 500000:
            risk_level = "MEDIUM"
            reason = "summarization still starts from the raw benchmark context and may hit backend limits"
    elif method == "srp":
        if max_memory_chars > 500000:
            risk_level = "MEDIUM"
            reason = "SRP may be safer than raw_prompt, but initial compression still touches the raw benchmark context"

    if risk_level == "LOW":
        return {
            "risk_level": risk_level,
            "model_name": model_name,
            "context_budget": budget,
            "max_memory_chars": max_memory_chars,
            "mean_memory_chars": mean_memory_chars,
            "max_query_chars": max_query_chars,
            "reason": "No obvious context-budget red flag detected for the selected method.",
        }

    return {
        "risk_level": risk_level,
        "model_name": model_name,
        "context_budget": budget,
        "max_memory_chars": max_memory_chars,
        "mean_memory_chars": mean_memory_chars,
        "max_query_chars": max_query_chars,
        "reason": reason,
    }


def confirm_context_risk(parent: tk.Tk, risk: dict) -> bool:
    if not risk or risk.get("risk_level") == "LOW":
        return True
    level = risk["risk_level"]
    message = (
        f"Context-budget precheck: {level} risk\n\n"
        f"Model: {risk['model_name']}\n"
        f"Known context budget: {risk['context_budget']} tokens\n"
        f"Max memory chars in selected group: {risk['max_memory_chars']}\n"
        f"Mean memory chars in selected group: {risk['mean_memory_chars']}\n"
        f"Max query chars: {risk['max_query_chars']}\n\n"
        f"Reason: {risk['reason']}\n\n"
        f"Do you still want to launch this batch?"
    )
    return messagebox.askyesno("Context-budget warning", message, parent=parent)


def write_generated_config(method: str, group_label: str, profile_label: str) -> Path:
    return write_generated_config_with_override(method, group_label, profile_label, None)


def write_generated_config_with_override(
    method: str,
    group_label: str,
    profile_label: str,
    output_root_override: str | None,
) -> tuple[Path, str]:
    profile = PROFILES[profile_label]
    task_file = GROUPS[group_label]
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    group_slug = slugify(group_label.split()[0])
    profile_slug = slugify(profile_label.split(":")[0])
    method_slug = slugify(method)
    session_slug = f"{method_slug}__{group_slug}__{profile_slug}__{timestamp}"
    slug = session_slug
    config_path = GENERATED_DIR / f"{slug}.json"
    output_root_base = output_root_override.strip() if output_root_override and output_root_override.strip() else profile["output_root_base"]
    output_root = f"{output_root_base.rstrip('/')}/{session_slug}"
    config = {
        "description": f"Generated launcher config for {method}, {group_label}, {profile_label}.",
        "shared": {
            "backend": DEFAULT_BACKEND,
            "task_file": task_file,
            "output_root": output_root,
            "repeats": profile["repeats"],
        },
        "runs": [
            {
                "name": f"launcher_{method_slug}_{group_slug}_{profile_slug}",
                "cycles": profile["cycles"],
                "models": [
                    DEFAULT_MODEL,
                ],
                "methods": [[method]],
            }
        ],
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config_path, output_root


def launch_batch(config_path: Path) -> None:
    script = ROOT / "run-longbench-batch-with-popup.ps1"
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-Config",
        str(config_path.relative_to(REPO_ROOT)),
    ]
    subprocess.Popen(command, cwd=REPO_ROOT)


def open_folder(path: str) -> None:
    try:
        os.startfile(path)
    except OSError as exc:
        messagebox.showerror("Open folder failed", str(exc))


def show_launch_dialog(parent: tk.Tk, method: str, group_label: str, profile_label: str, config_path: Path, output_root: str) -> None:
    dialog = tk.Toplevel(parent)
    dialog.title("Batch launched")
    dialog.geometry("620x260")
    dialog.minsize(620, 260)
    dialog.resizable(True, True)
    dialog.transient(parent)
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    text = (
        f"Launched:\nmode={method}\ngroup={group_label}\nprofile={profile_label}"
        f"\n\nGenerated config:\n{config_path}"
        f"\n\nResults root:\n{output_root}"
    )
    label = tk.Label(frame, text=text, justify="left", anchor="nw")
    label.grid(row=0, column=0, sticky="nsew")

    button_row = ttk.Frame(frame)
    button_row.grid(row=1, column=0, sticky="ew", pady=(12, 0))

    ttk.Button(
        button_row,
        text="Open Folder",
        command=lambda: open_folder(output_root),
    ).pack(side="left")

    ttk.Button(
        button_row,
        text="Close",
        command=dialog.destroy,
    ).pack(side="right")


def main() -> None:
    root = tk.Tk()
    root.title("SRP LongBench Launcher")
    root.geometry("620x420")
    root.minsize(620, 420)
    root.resizable(True, True)

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(6, weight=1)

    ttk.Label(frame, text="Mode").grid(row=0, column=0, sticky="w", pady=(0, 8))
    method_var = tk.StringVar(value=METHODS[0])
    method_box = ttk.Combobox(frame, textvariable=method_var, values=METHODS, state="readonly", width=34)
    method_box.grid(row=0, column=1, sticky="ew", pady=(0, 8))

    ttk.Label(frame, text="Task group").grid(row=1, column=0, sticky="w", pady=(0, 8))
    group_var = tk.StringVar(value=list(GROUPS.keys())[0])
    group_box = ttk.Combobox(frame, textvariable=group_var, values=list(GROUPS.keys()), state="readonly", width=34)
    group_box.grid(row=1, column=1, sticky="ew", pady=(0, 8))

    default_profile_label = list(PROFILES.keys())[0]

    ttk.Label(frame, text="Profile").grid(row=2, column=0, sticky="w", pady=(0, 8))
    profile_var = tk.StringVar(value=default_profile_label)
    profile_box = ttk.Combobox(frame, textvariable=profile_var, values=list(PROFILES.keys()), state="readonly", width=34)
    profile_box.grid(row=2, column=1, sticky="ew", pady=(0, 8))

    ttk.Label(frame, text="Output root override").grid(row=3, column=0, sticky="w", pady=(0, 8))
    output_root_var = tk.StringVar(value=PROFILES[default_profile_label]["output_root_base"])
    output_frame = ttk.Frame(frame)
    output_frame.grid(row=3, column=1, sticky="ew", pady=(0, 8))
    output_frame.columnconfigure(0, weight=1)

    output_root_entry = ttk.Entry(output_frame, textvariable=output_root_var, width=28)
    output_root_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    def choose_output_root() -> None:
        initial_dir = output_root_var.get().strip()
        chosen = filedialog.askdirectory(
            title="Select output root directory",
            initialdir=initial_dir or str(REPO_ROOT),
            mustexist=False,
        )
        if chosen:
            output_root_var.set(chosen)

    browse_button = ttk.Button(output_frame, text="Choose...", command=choose_output_root)
    browse_button.grid(row=0, column=1, sticky="e")

    ttk.Label(frame, text="SRP_TIMEOUT_SECONDS").grid(row=4, column=0, sticky="w", pady=(0, 8))
    timeout_var = tk.StringVar(value=os.getenv("SRP_TIMEOUT_SECONDS", "120"))
    timeout_frame = ttk.Frame(frame)
    timeout_frame.grid(row=4, column=1, sticky="ew", pady=(0, 8))
    timeout_frame.columnconfigure(0, weight=1)

    timeout_entry = ttk.Entry(timeout_frame, textvariable=timeout_var, width=18)
    timeout_entry.grid(row=0, column=0, sticky="w", padx=(0, 8))

    def save_timeout() -> None:
        raw = timeout_var.get().strip()
        if not raw.isdigit() or int(raw) <= 0:
            messagebox.showerror("Invalid timeout", "SRP_TIMEOUT_SECONDS must be a positive integer.")
            return
        update_env_value("SRP_TIMEOUT_SECONDS", raw)
        messagebox.showinfo("Saved", f"Saved SRP_TIMEOUT_SECONDS={raw} to {ENV_PATH}")

    ttk.Button(timeout_frame, text="Save Timeout", command=save_timeout).grid(row=0, column=1, sticky="w")

    ttk.Label(frame, text="SRP_MODEL_CONTEXT_BUDGET").grid(row=5, column=0, sticky="w", pady=(0, 8))
    context_budget_var = tk.StringVar(value=os.getenv("SRP_MODEL_CONTEXT_BUDGET", "1024"))
    context_frame = ttk.Frame(frame)
    context_frame.grid(row=5, column=1, sticky="ew", pady=(0, 8))
    context_frame.columnconfigure(0, weight=1)

    context_entry = ttk.Entry(context_frame, textvariable=context_budget_var, width=18)
    context_entry.grid(row=0, column=0, sticky="w", padx=(0, 8))

    def save_context_budget() -> None:
        raw = context_budget_var.get().strip()
        if not raw.isdigit() or int(raw) <= 0:
            messagebox.showerror("Invalid context budget", "SRP_MODEL_CONTEXT_BUDGET must be a positive integer.")
            return
        update_env_value("SRP_MODEL_CONTEXT_BUDGET", raw)
        messagebox.showinfo("Saved", f"Saved SRP_MODEL_CONTEXT_BUDGET={raw} to {ENV_PATH}")

    ttk.Button(context_frame, text="Save Context Budget", command=save_context_budget).grid(row=0, column=1, sticky="w")

    info = tk.Text(frame, height=12, width=72, wrap="word")
    info.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(8, 12))
    info.configure(state="disabled")

    def refresh_info(*_args) -> None:
        method = method_var.get()
        group_label = group_var.get()
        profile = PROFILES[profile_var.get()]
        task_file = GROUPS[group_label]
        output_root_base = output_root_var.get().strip() or profile["output_root_base"]
        text = (
            f"Selected mode: {method}\n"
            f"Selected group: {group_label}\n"
            f"Task file: {task_file}\n"
            f"Cycles: {profile['cycles']}\n"
            f"Repeats: {profile['repeats']}\n"
            f"Output root base: {output_root_base}\n"
            f"Backend: {DEFAULT_BACKEND}\n"
            f"Model: {DEFAULT_MODEL}\n"
            f"Context budget: {context_budget_var.get().strip() or get_context_budget(DEFAULT_MODEL) or 'unknown'}\n"
            f"Timeout seconds: {timeout_var.get().strip() or os.getenv('SRP_TIMEOUT_SECONDS', '120')}\n"
            f"Repeat folders: r01 ... r{profile['repeats']:02d}\n"
            f"Progress popup: enabled"
        )
        info.configure(state="normal")
        info.delete("1.0", "end")
        info.insert("1.0", text)
        info.configure(state="disabled")

    def sync_output_root_with_profile(*_args) -> None:
        current = output_root_var.get().strip()
        profile_default = PROFILES[profile_var.get()]["output_root_base"]
        if not current or current in PROFILE_DEFAULTS:
            output_root_var.set(profile_default)

    def on_launch() -> None:
        method = method_var.get()
        group_label = group_var.get()
        profile_label = profile_var.get()
        task_file = GROUPS[group_label]
        model_name = DEFAULT_MODEL
        risk = estimate_prompt_risk(method, task_file, model_name)
        if not confirm_context_risk(root, risk):
            return
        try:
            config_path, output_root = write_generated_config_with_override(
                method,
                group_label,
                profile_label,
                output_root_var.get(),
            )
            launch_batch(config_path)
        except Exception as exc:
            messagebox.showerror("Launch failed", str(exc))
            return
        show_launch_dialog(root, method, group_label, profile_label, config_path, output_root)

    profile_var.trace_add("write", sync_output_root_with_profile)

    for variable in (method_var, group_var, profile_var, output_root_var, timeout_var, context_budget_var):
        variable.trace_add("write", refresh_info)

    launch_button = ttk.Button(frame, text="Launch batch", command=on_launch)
    launch_button.grid(row=7, column=0, columnspan=2, sticky="ew")

    refresh_info()
    root.mainloop()


if __name__ == "__main__":
    main()
