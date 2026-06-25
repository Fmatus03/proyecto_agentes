from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

from .constants import ROOT
from .orchestrator import OrchestratorGraph, latest_run
from .registry import agent_registry, tool_registry
from .utils import read_json, write_json


def _project(path: str) -> Path:
    return Path(path).resolve()


def cmd_init_project(args: argparse.Namespace) -> int:
    project_dir = _project(args.project)
    OrchestratorGraph(factory_root=ROOT, project_dir=project_dir).initialize_project()
    write_json(project_dir / "tool-availability.json", detect_tools())
    print(f"project_ready={project_dir}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    project_dir = _project(args.project)
    run_dir = OrchestratorGraph(factory_root=ROOT, project_dir=project_dir).run(args.objective)
    write_json(project_dir / "latest-run.json", {"run_dir": str(run_dir)})
    print(f"run_dir={run_dir}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project_dir = _project(args.project)
    run_dir = Path(args.run).resolve() if args.run else latest_run(project_dir)
    if run_dir is None:
        print("error=no_run_found")
        return 2
    result = verify_run(run_dir)
    write_json(run_dir / "verification-summary.json", result)
    print(f"status={result['status']}")
    print(f"run_dir={run_dir}")
    if result["missing"]:
        print("missing=" + ",".join(result["missing"]))
    return 0 if result["status"] == "complete" else 1


def cmd_list(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {
        "agents": sorted(agent_registry()),
        "tools": sorted(tool_registry()),
    }
    write_json(Path(args.output).resolve(), payload) if args.output else print(payload)
    return 0


def detect_tools() -> dict[str, Any]:
    detected = {}
    for tool_id, spec in tool_registry().items():
        if spec.available_command:
            detected[tool_id] = {
                "command": spec.available_command,
                "available": shutil.which(spec.available_command) is not None,
            }
        else:
            detected[tool_id] = {"command": None, "available": True}
    return detected


def verify_run(run_dir: Path) -> dict[str, Any]:
    required = [
        "work_order.json",
        "state.json",
        "spec.md",
        "clarifications.md",
        "checklist.md",
        "context-pack.json",
        "context-pack.md",
        "evidence-register.json",
        "plan.md",
        "contracts.md",
        "tasks.md",
        "analyze-report.json",
        "test-plan.md",
        "test-report.md",
        "coverage-report.json",
        "security-review.md",
        "validation-report.json",
        "traceability-matrix.md",
        "final-report.json",
        "RUN_STATE.md",
        "DECISIONS.md",
        "ERRORS.md",
        "billing-ledger.json",
        "CHECKLIST_APLICADO.md",
    ]
    missing = [name for name in required if not (run_dir / name).exists()]
    agents_json = run_dir / "registries" / "agents.json"
    tools_json = run_dir / "registries" / "tools.json"
    skills_json = run_dir / "registries" / "skills.json"
    if not agents_json.exists():
        missing.append("registries/agents.json")
    if not tools_json.exists():
        missing.append("registries/tools.json")
    if not skills_json.exists():
        missing.append("registries/skills.json")
    final_status = "error"
    if (run_dir / "final-report.json").exists():
        final_status = read_json(run_dir / "final-report.json").get("status", "error")
    status = "complete" if not missing and final_status == "complete" else "error"
    return {
        "status": status,
        "run_dir": str(run_dir),
        "missing": missing,
        "final_status": final_status,
        "agents_registered": len(read_json(agents_json)) if agents_json.exists() else 0,
        "tools_registered": len(read_json(tools_json)) if tools_json.exists() else 0,
        "skills_registered": len(read_json(skills_json)) if skills_json.exists() else 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fabrica Web ARNES SDD")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-project")
    init.add_argument("--project", default="project")
    init.set_defaults(func=cmd_init_project)

    run = sub.add_parser("run")
    run.add_argument("--project", default="project")
    run.add_argument("--objective", required=True)
    run.set_defaults(func=cmd_run)

    verify = sub.add_parser("verify")
    verify.add_argument("--project", default="project")
    verify.add_argument("--run")
    verify.set_defaults(func=cmd_verify)

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--output")
    list_cmd.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
