from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HumanEvalExecutionResult:
    task_id: str
    variant: str
    passed: bool
    stdout: str = ""
    stderr: str = ""
    execution_time_seconds: float = 0.0
    failure_category: str | None = None
    failure_message: str | None = None
    return_code: int | None = None
    sandbox_policy: str = "subprocess_isolation_v1"
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class HumanEvalExecutor:
    def _safe_task_prefix(self, task_id: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(task_id).strip())
        return safe[:64] or "task"

    def __init__(
        self,
        *,
        timeout_seconds: float = 5.0,
        sandbox_policy: str = "subprocess_isolation_v1",
        allow_network: bool = False,
    ) -> None:
        self.timeout_seconds = float(timeout_seconds)
        self.sandbox_policy = sandbox_policy
        self.allow_network = bool(allow_network)

    def _build_bootstrap(self, payload_path: Path) -> str:
        return textwrap.dedent(
            f"""
            import contextlib
            import io
            import json
            import time
            import traceback
            from pathlib import Path

            payload = json.loads(Path({str(payload_path)!r}).read_text(encoding="utf-8"))
            generated_code = str(payload.get("generated_code", ""))
            test_specification = str(payload.get("test_specification", ""))

            stdout = io.StringIO()
            stderr = io.StringIO()
            namespace = {{"__name__": "__main__"}}
            started = time.perf_counter()
            passed = False
            failure_category = None
            failure_message = None
            return_code = 0

            try:
                candidate = compile(generated_code, "<generated_code>", "exec")
                tests = compile(test_specification, "<test_specification>", "exec")
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exec(candidate, namespace)
                    exec(tests, namespace)
                passed = True
            except AssertionError as exc:
                failure_category = "failed_assertion"
                failure_message = str(exc) or "assertion failed"
                return_code = 1
            except SyntaxError as exc:
                failure_category = "syntax_error"
                failure_message = f"{{exc.msg}} (line {{exc.lineno}})"
                return_code = 1
            except Exception as exc:
                failure_category = "runtime_error"
                failure_message = f"{{type(exc).__name__}}: {{exc}}"
                return_code = 1

            result = {{
                "passed": passed,
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "execution_time_seconds": round(time.perf_counter() - started, 6),
                "failure_category": failure_category,
                "failure_message": failure_message,
                "return_code": return_code,
            }}
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            """
        ).strip()

    def execute(
        self,
        *,
        task_id: str,
        variant: str,
        generated_code: str,
        test_specification: str,
        metadata: dict[str, Any] | None = None,
    ) -> HumanEvalExecutionResult:
        metadata = dict(metadata or {})
        with tempfile.TemporaryDirectory(prefix=f"humaneval_{self._safe_task_prefix(task_id)}_") as tmp:
            tmp_path = Path(tmp)
            payload_path = tmp_path / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "generated_code": generated_code,
                        "test_specification": test_specification,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            bootstrap_path = tmp_path / "bootstrap.py"
            bootstrap_path.write_text(self._build_bootstrap(payload_path), encoding="utf-8")
            started = time.perf_counter()
            environment = dict(os.environ)
            environment.update(
                {
                    "PYTHONNOUSERSITE": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONHASHSEED": "0",
                    "PATH": str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", ""),
                }
            )
            try:
                completed = subprocess.run(
                    [sys.executable, "-I", str(bootstrap_path)],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                    env=environment,
                )
            except subprocess.TimeoutExpired as exc:
                elapsed = round(time.perf_counter() - started, 6)
                return HumanEvalExecutionResult(
                    task_id=task_id,
                    variant=variant,
                    passed=False,
                    stdout=str(getattr(exc, "stdout", "") or ""),
                    stderr=str(getattr(exc, "stderr", "") or ""),
                    execution_time_seconds=elapsed,
                    failure_category="timeout",
                    failure_message=f"timeout after {self.timeout_seconds} seconds",
                    return_code=None,
                    sandbox_policy=self.sandbox_policy,
                    metadata={**metadata, "allow_network": self.allow_network},
                )

            elapsed = round(time.perf_counter() - started, 6)
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            try:
                parsed = json.loads(stdout or "{}")
            except json.JSONDecodeError:
                return HumanEvalExecutionResult(
                    task_id=task_id,
                    variant=variant,
                    passed=False,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time_seconds=elapsed,
                    failure_category="sandbox_error",
                    failure_message="executor did not return JSON",
                    return_code=completed.returncode,
                    sandbox_policy=self.sandbox_policy,
                    metadata={**metadata, "allow_network": self.allow_network},
                )
            return HumanEvalExecutionResult(
                task_id=task_id,
                variant=variant,
                passed=bool(parsed.get("passed")),
                stdout=str(parsed.get("stdout", "")),
                stderr=str(parsed.get("stderr", "")),
                execution_time_seconds=float(parsed.get("execution_time_seconds", elapsed)),
                failure_category=parsed.get("failure_category"),
                failure_message=parsed.get("failure_message"),
                return_code=int(parsed.get("return_code", completed.returncode)),
                sandbox_policy=self.sandbox_policy,
                metadata={**metadata, "allow_network": self.allow_network},
            )
