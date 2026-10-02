"""Freeze code/data and audit a repeat without modifying historical evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from report_conversation_eval import paired


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    directory, previous = args.directory, args.previous
    paths = sorted(set(Path("backend/app").rglob("*.py")) |
                   set(Path("data").rglob("*.csv")) |
                   set(Path("backend").rglob("active_collection.json")) |
                   set(Path("data").rglob("*.md")))
    fingerprint = {str(p): digest(p) for p in paths}
    frozen = {name: digest(directory / name) == digest(previous / name)
              for name in ("cases.json", "baseline_workspace.py", "freeze.json")}
    if not all(frozen.values()):
        raise SystemExit("Frozen inputs differ from historical evaluation")
    if args.freeze:
        target = directory / "code-and-data-fingerprint.json"
        if target.exists():
            raise SystemExit("Refusing to overwrite existing freeze")
        result = {"utc": datetime.now(timezone.utc).isoformat(), "files": fingerprint,
                  "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                  "frozen_inputs_identical": frozen}
    else:
        initial = json.loads((directory / "code-and-data-fingerprint.json").read_text())
        changes = [p for p in initial["files"] if fingerprint.get(p) != initial["files"][p]]
        records = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
        historical = [json.loads(line) for line in (previous / "raw.jsonl").read_text().splitlines()]
        turns = [r for r in records if r["kind"] == "turn"]
        pairs = []
        for phase in ("finish", "recheck", "legacy_recheck"):
            grouped = {(r["case_id"], r["repetition"], r["arm"]): r for r in turns if r["phase"] == phase}
            for (case, rep, arm), form in grouped.items():
                if arm != "after_form":
                    continue
                text = grouped.get((case, rep, "after_same_text"))
                if text is None:
                    continue
                def hashes(row):
                    return [c.get("input_sha256") for c in row["calls"] if c["stage"] == "classification"]
                pairs.append({"phase": phase, "case_id": case, "repetition": rep,
                              "identical_prompt": bool(hashes(form)) and hashes(form) == hashes(text),
                              "same_class": form["classification"] == text["classification"],
                              "both_idle": form["status"] == text["status"] == "idle"})
        old_integrity = json.loads((previous / "final-integrity.json").read_text())
        previous_intact = all(digest(previous / name) == sha for name, sha in old_integrity["artifacts_sha256"].items())
        result = {"utc": datetime.now(timezone.utc).isoformat(), "frozen_inputs_identical": frozen,
                  "source_or_data_changed_during_run": changes, "historical_artifacts_intact": previous_intact,
                  "research_data_unchanged_from_start_commit": subprocess.run(
                      ["git", "diff", "--quiet", initial["head"], "--", "data", "backend/data", "backend/chroma_db/active_collection.json"]).returncode == 0,
                  "final_tools_sha256": {str(p): digest(p) for p in (
                      Path("scripts/run_conversation_eval.py"), Path("scripts/report_conversation_eval.py"),
                      Path("scripts/smoke_workspace_followup.py"), Path(__file__))},
                  "collection_names": sorted({r["collection"] for r in records if r["kind"] == "environment"}),
                  "channel_pairs": pairs,
                  "historical_pr16_vs_corrected": paired(
                      [r for r in historical if r["kind"] == "turn" and r["phase"] == "baseline" and r["arm"] == "after"],
                      [r for r in turns if r["phase"] == "baseline" and r["arm"] == "after"]),
                  "artifacts_sha256": {p.name: digest(p) for p in directory.iterdir() if p.is_file() and p.name != "final-integrity.json"}}
        target = directory / "final-integrity.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
