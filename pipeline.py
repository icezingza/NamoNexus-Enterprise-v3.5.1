#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional


DEFAULT_MODELS = ["claude-opus-4.5", "gemini-3-pro", "gpt-oss-120b"]
DEFAULT_PROMPTS_FILE = "prompts.json"
DEFAULT_REPORT_FILE = "triage_reliability_report.md"
DEFAULT_GEMINI_OUTPUT = os.path.join("reports", "geminicli_report.md")


def log(message: str) -> None:
    print(message, flush=True)


def parse_models(raw: Optional[str]) -> List[str]:
    if not raw:
        return list(DEFAULT_MODELS)
    return [item.strip() for item in raw.split(",") if item.strip()]


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_command(
    cmd: List[str],
    cwd: Path,
    check: bool = False,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=check,
        text=True,
        capture_output=capture_output,
    )


def run_tests(repo_root: Path) -> None:
    log("Running tests...")
    run_command(
        [sys.executable, "-m", "pytest", "--maxfail=1", "--disable-warnings", "-q"],
        cwd=repo_root,
        check=False,
    )


def collect_logs(repo_root: Path) -> Optional[Path]:
    log("Collecting logs...")
    logs_dir = repo_root / "logs"
    if not logs_dir.exists():
        log(f"No logs directory found at {logs_dir}. Skipping log collection.")
        return None

    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = reports_dir / f"logs_snapshot_{timestamp}.zip"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in logs_dir.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(repo_root))

    log(f"Log snapshot written to {archive_path}")
    return archive_path


def run_geminicli_batch(
    repo_root: Path,
    gemini_cli: str,
    prompts_file: Path,
    output_file: Path,
) -> Optional[Path]:
    log("Running GeminiCLI batch...")
    if not command_exists(gemini_cli):
        log(f"GeminiCLI not found in PATH ({gemini_cli}). Skipping.")
        return None
    if not prompts_file.exists():
        log(f"Prompts file not found at {prompts_file}. Skipping.")
        return None

    output_file.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [gemini_cli, "run", "--input", str(prompts_file), "--output", str(output_file)],
        cwd=repo_root,
        check=False,
    )
    return output_file


def load_prompts(prompts_file: Path) -> List[str]:
    with prompts_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    prompts: List[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                text = item.strip()
            elif isinstance(item, dict):
                text = str(item.get("text", "")).strip()
            else:
                continue
            if text:
                prompts.append(text)
    else:
        raise ValueError("prompts.json must be a list of strings or objects with a 'text' field.")

    if not prompts:
        raise ValueError("prompts.json contains no usable prompts.")
    return prompts


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def shorten(text: str, limit: int = 80) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def run_ai_analysis(
    repo_root: Path,
    gemini_cli: str,
    models: Iterable[str],
    prompts_file: Path,
    report_file: Path,
    gemini_output: Optional[Path],
) -> Optional[Path]:
    log("Running AI analysis...")
    if not command_exists(gemini_cli):
        log(f"GeminiCLI not found in PATH ({gemini_cli}). Skipping.")
        return None
    if not prompts_file.exists():
        log(f"Prompts file not found at {prompts_file}. Skipping.")
        return None

    try:
        prompts = load_prompts(prompts_file)
    except ValueError as exc:
        log(f"Invalid prompts file: {exc}")
        return None

    results = []
    for model in models:
        for prompt in prompts:
            start = time.perf_counter()
            cmd = [gemini_cli, "run", "--model", model, "--prompt", prompt]
            completed = run_command(cmd, cwd=repo_root, capture_output=True, check=False)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            stdout = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()

            status = "OK" if completed.returncode == 0 else "ERROR"
            response = stdout
            error = ""
            if completed.returncode != 0:
                response = ""
                error = stderr or stdout or f"geminicli exited with code {completed.returncode}"

            results.append(
                {
                    "model": model,
                    "prompt": prompt,
                    "status": status,
                    "elapsed_ms": elapsed_ms,
                    "response": response,
                    "error": error,
                }
            )

    timestamp = dt.datetime.now().isoformat(timespec="seconds")
    report_lines = [
        "# Triage Reliability Report",
        "",
        f"Timestamp: {timestamp}",
        f"Prompts file: {prompts_file}",
        f"Models: {', '.join(models)}",
    ]
    if gemini_output:
        report_lines.append(f"GeminiCLI output: {gemini_output}")
    report_lines.extend(
        [
            "",
            "## Summary",
            "| Model | Prompt | Status | ms |",
            "| --- | --- | --- | --- |",
        ]
    )

    for item in results:
        report_lines.append(
            "| {model} | {prompt} | {status} | {elapsed_ms} |".format(
                model=item["model"],
                prompt=md_escape(shorten(item["prompt"])),
                status=item["status"],
                elapsed_ms=item["elapsed_ms"],
            )
        )

    report_lines.extend(["", "## Details", ""])
    for item in results:
        report_lines.append(f"### {item['model']}")
        report_lines.append(f"- Prompt: {item['prompt']}")
        report_lines.append(f"- Status: {item['status']}")
        report_lines.append(f"- Elapsed_ms: {item['elapsed_ms']}")
        if item["response"]:
            report_lines.extend(["", "Response:", "", "```text", item["response"], "```"])
        if item["error"]:
            report_lines.extend(["", "Error:", "", "```text", item["error"], "```"])
        report_lines.append("")

    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    log(f"Report written to {report_file}")
    return report_file


def run_antigravity(repo_root: Path) -> None:
    log("Running antigravity...")
    run_command([sys.executable, "-m", "antigravity"], cwd=repo_root, check=False)


def git_has_changes(repo_root: Path, path: Path) -> bool:
    status = run_command(
        ["git", "-C", str(repo_root), "status", "--porcelain", "--", str(path)],
        cwd=repo_root,
        capture_output=True,
        check=False,
    ).stdout.strip()
    return bool(status)


def commit_and_push(repo_root: Path, report_file: Path) -> None:
    log("Committing and pushing to GitHub...")
    if not (repo_root / ".git").exists():
        log("No .git directory found. Skipping git step.")
        return
    if not command_exists("git"):
        log("git is not available in PATH. Skipping git step.")
        return
    if not report_file.exists():
        log(f"Report file not found at {report_file}. Skipping git step.")
        return

    if not git_has_changes(repo_root, report_file):
        log("No report changes to commit. Skipping git commit/push.")
        return

    run_command(["git", "-C", str(repo_root), "add", str(report_file)], cwd=repo_root)
    run_command(
        ["git", "-C", str(repo_root), "commit", "-m", "Auto: update reliability report"],
        cwd=repo_root,
        check=False,
    )
    run_command(["git", "-C", str(repo_root), "push"], cwd=repo_root, check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full NamoNexus pipeline.")
    parser.add_argument("--repo", default="", help="Override repo root (default: script directory).")
    parser.add_argument("--prompts", default=DEFAULT_PROMPTS_FILE, help="Path to prompts.json.")
    parser.add_argument("--report", default=DEFAULT_REPORT_FILE, help="Output report filename.")
    parser.add_argument("--models", default="", help="Comma-separated list of model IDs.")
    parser.add_argument("--gemini-cli", default="geminicli", help="GeminiCLI binary name.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest.")
    parser.add_argument("--skip-logs", action="store_true", help="Skip log snapshot.")
    parser.add_argument("--skip-gemini", action="store_true", help="Skip GeminiCLI batch.")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip AI analysis.")
    parser.add_argument("--skip-antigravity", action="store_true", help="Skip antigravity.")
    parser.add_argument("--skip-git", action="store_true", help="Skip git commit/push.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parent
    prompts_file = (repo_root / args.prompts).resolve()
    report_file = (repo_root / args.report).resolve()
    gemini_output = (repo_root / DEFAULT_GEMINI_OUTPUT).resolve()
    models = parse_models(args.models)

    if not args.skip_tests:
        run_tests(repo_root)
    if not args.skip_logs:
        collect_logs(repo_root)
    gemini_output_path: Optional[Path] = None
    if not args.skip_gemini:
        gemini_output_path = run_geminicli_batch(
            repo_root, args.gemini_cli, prompts_file, gemini_output
        )
    if not args.skip_analysis:
        run_ai_analysis(
            repo_root,
            args.gemini_cli,
            models,
            prompts_file,
            report_file,
            gemini_output_path,
        )
    if not args.skip_antigravity:
        run_antigravity(repo_root)
    if not args.skip_git:
        commit_and_push(repo_root, report_file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
