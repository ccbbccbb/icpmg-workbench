# /// script
# dependencies = []
# ///

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RANKINGS_PATH = ROOT / "outputs" / "candidate_rankings.json"
MANIFEST_PATH = ROOT / "resume_role_assignments.json"
OUTPUT_JSON = ROOT / "outputs" / "workbench_candidate_snapshots.json"
OUTPUT_CSV = ROOT / "outputs" / "workbench_candidate_snapshots.csv"

ROLE_TO_JOB_ID = {
    "ai_builder_senior_consultant": "32538",
    "ai_builder_manager": "32544",
    "data_ai_alliance_exec": "30989",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export compact candidate snapshots for the Next.js workbench.")
    parser.add_argument("--rankings", type=Path, default=RANKINGS_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--json-output", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--csv-output", type=Path, default=OUTPUT_CSV)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def display_name(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("_"))


def review_band(score: float) -> str:
    if score >= 85:
        return "Strong match"
    if score >= 65:
        return "Review"
    if score >= 40:
        return "Partial match"
    return "Low alignment"


def top_highlights(score: dict[str, Any], limit: int = 4) -> list[dict[str, Any]]:
    highlights = []
    for requirement in score["matched_requirements"][:limit]:
        highlights.append(
            {
                "label": requirement["label"],
                "priority": requirement["priority"],
                "matchedTerms": requirement["matched_terms"][:5],
                "evidence": requirement["snippets"][:2],
            }
        )
    return highlights


def profile_path(candidate: str) -> str:
    return f"{candidate}/{candidate}_profile.png"


def resume_path(candidate: str) -> str:
    return f"{candidate}/{candidate}_resume.txt"


def build_snapshot(item: dict[str, Any], expected_job_id: str) -> dict[str, Any]:
    scores = {score["job_id"]: score for score in item["scores"]}
    applied_score = scores[expected_job_id]
    best_score = item["scores"][0]
    return {
        "candidateId": item["candidate"],
        "candidateName": display_name(item["candidate"]),
        "appliedJobId": expected_job_id,
        "recommendedJobId": item["best_job_id"],
        "recommendedRole": item["best_role"],
        "score": applied_score["score"],
        "scoreBeforePenalty": applied_score["score_before_penalty"],
        "reviewBand": review_band(applied_score["score"]),
        "isCrossRoleRecommendation": item["best_job_id"] != expected_job_id,
        "crossRoleDelta": round(best_score["score"] - applied_score["score"], 2),
        "profileImagePath": profile_path(item["candidate"]),
        "resumePath": resume_path(item["candidate"]),
        "yearsReason": applied_score["years_reason"],
        "titleMatches": applied_score["title_matches"],
        "prototypePortfolio": applied_score["portfolio_reason"],
        "highlights": top_highlights(applied_score),
        "missingCritical": applied_score["missing_critical"][:5],
        "missingStrong": applied_score["missing_strong"][:5],
        "riskFlags": [penalty["label"] for penalty in applied_score["penalties"]],
        "scoresByJob": {score["job_id"]: score["score"] for score in item["scores"]},
    }


def write_csv(grouped: dict[str, list[dict[str, Any]]], path: Path) -> None:
    fieldnames = [
        "appliedJobId",
        "rank",
        "candidateId",
        "candidateName",
        "score",
        "reviewBand",
        "recommendedJobId",
        "isCrossRoleRecommendation",
        "crossRoleDelta",
        "topHighlight",
        "missingCritical",
        "riskFlags",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for job_id, candidates in grouped.items():
            for rank, candidate in enumerate(candidates, start=1):
                writer.writerow(
                    {
                        "appliedJobId": job_id,
                        "rank": rank,
                        "candidateId": candidate["candidateId"],
                        "candidateName": candidate["candidateName"],
                        "score": candidate["score"],
                        "reviewBand": candidate["reviewBand"],
                        "recommendedJobId": candidate["recommendedJobId"],
                        "isCrossRoleRecommendation": candidate["isCrossRoleRecommendation"],
                        "crossRoleDelta": candidate["crossRoleDelta"],
                        "topHighlight": candidate["highlights"][0]["label"] if candidate["highlights"] else "",
                        "missingCritical": "; ".join(candidate["missingCritical"]),
                        "riskFlags": "; ".join(candidate["riskFlags"]),
                    }
                )


def main() -> None:
    args = parse_args()
    rankings = load_json(args.rankings)
    manifest = load_json(args.manifest)
    applied_job_by_candidate = {
        item["folder"]: ROLE_TO_JOB_ID[item["target_role"]]
        for item in manifest
    }

    grouped: dict[str, list[dict[str, Any]]] = {job_id: [] for job_id in ROLE_TO_JOB_ID.values()}
    for item in rankings:
        expected_job_id = applied_job_by_candidate[item["candidate"]]
        grouped[expected_job_id].append(build_snapshot(item, expected_job_id))

    for candidates in grouped.values():
        candidates.sort(key=lambda candidate: candidate["score"], reverse=True)

    payload = {
        "schemaVersion": "1.0",
        "generatedFrom": {
            "rankings": str(args.rankings.relative_to(ROOT)),
            "manifest": str(args.manifest.relative_to(ROOT)),
        },
        "jobs": grouped,
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_csv(grouped, args.csv_output)

    print(f"Snapshot jobs: {len(grouped)}")
    for job_id, candidates in grouped.items():
        print(f"{job_id}: {len(candidates)} candidates")
    print(f"JSON output: {args.json_output}")
    print(f"CSV output: {args.csv_output}")


if __name__ == "__main__":
    main()
