# /// script
# dependencies = []
# ///

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REQUIREMENTS_PATH = ROOT / "job_descriptions" / "job_requirements.json"
SIGNALS_PATH = ROOT / "outputs" / "cv_signal_extracts.json"
OUTPUT_DIR = ROOT / "outputs"
DETAIL_OUTPUT = OUTPUT_DIR / "candidate_rankings.json"
CSV_OUTPUT = OUTPUT_DIR / "candidate_rankings.csv"
VALIDATION_OUTPUT = OUTPUT_DIR / "ranking_validation.json"
GROUND_TRUTH_PATH = ROOT / "resume_role_assignments.json"

YEARS_WEIGHT = 8
TITLE_WEIGHT = 6
PORTFOLIO_WEIGHT = 4
MANAGER_SENIORITY_BONUS = 8
SENIOR_CONSULTANT_MANAGER_PENALTY = 10

MANAGER_TITLE_TERMS = [
    "manager",
    "lead",
    "program manager",
    "project manager",
    "product owner",
    "delivery lead",
    "head",
    "director",
]

HANDS_ON_TITLE_TERMS = [
    "consultant",
    "engineer",
    "developer",
    "analyst",
    "specialist",
    "builder",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank extracted candidate CV signals against the three job descriptions.")
    parser.add_argument("--requirements", type=Path, default=REQUIREMENTS_PATH)
    parser.add_argument("--signals", type=Path, default=SIGNALS_PATH)
    parser.add_argument("--json-output", type=Path, default=DETAIL_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=CSV_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=VALIDATION_OUTPUT)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def title_score(candidate: dict[str, Any], job: dict[str, Any]) -> tuple[float, list[str]]:
    titles = " ".join(candidate["experience"]["titles"]).lower().replace("&", "and")
    matches = []
    for term in job.get("title_terms", []):
        if term.lower().replace("&", "and") in titles:
            matches.append(term)
    if not matches:
        return 0.0, []
    return TITLE_WEIGHT, matches


def years_score(candidate: dict[str, Any], job: dict[str, Any]) -> tuple[float, str]:
    years = candidate["experience"]["total_experience_years"]
    minimum = job.get("minimum_years", 0)
    if minimum <= 0:
        return YEARS_WEIGHT, f"{years} years detected"
    ratio = min(1.0, years / minimum)
    return YEARS_WEIGHT * ratio, f"{years}/{minimum} years detected"


def portfolio_score(candidate: dict[str, Any], job: dict[str, Any]) -> tuple[float, str | None]:
    if job.get("family") != "ai_builder":
        return 0.0, None
    has_url = bool(candidate["contact"]["urls"])
    sections = set(candidate["sections_present"])
    has_portfolio_section = "AGENTIC AI BUILD LEADERSHIP" in sections or "AGENTIC AI BUILD PORTFOLIO" in sections
    if has_url and has_portfolio_section:
        return PORTFOLIO_WEIGHT, "prototype portfolio URL and agentic AI build section"
    if has_url or has_portfolio_section:
        return PORTFOLIO_WEIGHT * 0.5, "partial prototype portfolio evidence"
    return 0.0, None


def seniority_adjustment(candidate: dict[str, Any], job_id: str) -> tuple[float, str | None]:
    title_text = " ".join(candidate["experience"]["titles"]).lower()
    has_manager_signal = any(term in title_text for term in MANAGER_TITLE_TERMS)
    has_hands_on_signal = any(term in title_text for term in HANDS_ON_TITLE_TERMS)
    if job_id == "32544" and has_manager_signal:
        return MANAGER_SENIORITY_BONUS, "manager-level title or leadership signal"
    if job_id == "32538" and has_manager_signal and not has_hands_on_signal:
        return -SENIOR_CONSULTANT_MANAGER_PENALTY, "manager-level title without hands-on consultant/engineer signal"
    if job_id == "32538" and "manager" in title_text:
        return -(SENIOR_CONSULTANT_MANAGER_PENALTY * 0.6), "manager title is stronger fit for Manager role"
    return 0.0, None


def requirement_score(requirement: dict[str, Any], match: dict[str, Any] | None) -> tuple[float, dict[str, Any] | None]:
    if not match:
        return 0.0, None
    min_hits = max(1, requirement.get("min_hits", 1))
    unique_terms = match["unique_terms"]
    total_hits = match["total_hits"]
    coverage = min(1.0, unique_terms / min_hits)
    repetition_bonus = min(0.2, max(0, total_hits - unique_terms) * 0.03)
    score = requirement["weight"] * min(1.0, coverage + repetition_bonus)
    snippets = []
    for term in match["terms"][:3]:
        for snippet in term.get("snippets", [])[:1]:
            if snippet not in snippets:
                snippets.append(snippet)
    evidence = {
        "id": requirement["id"],
        "label": requirement["label"],
        "priority": requirement["priority"],
        "score": round(score, 2),
        "weight": requirement["weight"],
        "unique_terms": unique_terms,
        "total_hits": total_hits,
        "matched_terms": [term["term"] for term in match["terms"]],
        "snippets": snippets,
    }
    return score, evidence


def score_candidate_for_job(candidate: dict[str, Any], job_id: str, job: dict[str, Any]) -> dict[str, Any]:
    candidate_matches = {
        item["id"]: item for item in candidate["job_requirement_hits"][job_id]["matched_requirements"]
    }
    total_possible = sum(req["weight"] for req in job["requirements"]) + YEARS_WEIGHT + TITLE_WEIGHT
    if job.get("family") == "ai_builder":
        total_possible += PORTFOLIO_WEIGHT

    raw_score = 0.0
    matched_evidence = []
    missing_critical = []
    missing_strong = []

    for requirement in job["requirements"]:
        score, evidence = requirement_score(requirement, candidate_matches.get(requirement["id"]))
        raw_score += score
        if evidence:
            matched_evidence.append(evidence)
        elif requirement["priority"] == "critical":
            missing_critical.append(requirement["label"])
        elif requirement["priority"] == "strong":
            missing_strong.append(requirement["label"])

    years_points, years_reason = years_score(candidate, job)
    raw_score += years_points

    title_points, title_matches = title_score(candidate, job)
    raw_score += title_points

    portfolio_points, portfolio_reason = portfolio_score(candidate, job)
    raw_score += portfolio_points
    seniority_points, seniority_reason = seniority_adjustment(candidate, job_id)

    penalties = []
    penalty_points = 0.0
    for indicator in candidate["negative_indicators"]:
        penalty_points += indicator["penalty"]
        penalties.append({"label": indicator["label"], "penalty": indicator["penalty"], "terms": indicator["terms"]})

    normalized_before_penalty = (raw_score / total_possible) * 100
    final_score = max(0.0, min(100.0, normalized_before_penalty - penalty_points + seniority_points))

    matched_evidence.sort(key=lambda item: item["score"], reverse=True)
    return {
        "job_id": job_id,
        "role": job["role"],
        "score": round(final_score, 2),
        "score_before_penalty": round(normalized_before_penalty, 2),
        "penalty_points": round(penalty_points, 2),
        "years_score": round(years_points, 2),
        "years_reason": years_reason,
        "title_score": round(title_points, 2),
        "title_matches": title_matches,
        "portfolio_score": round(portfolio_points, 2),
        "portfolio_reason": portfolio_reason,
        "seniority_adjustment": round(seniority_points, 2),
        "seniority_reason": seniority_reason,
        "matched_requirements": matched_evidence,
        "matched_requirement_count": len(matched_evidence),
        "missing_critical": missing_critical,
        "missing_strong": missing_strong,
        "penalties": penalties,
    }


def rank_candidates(requirements: dict[str, Any], signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for candidate in signals:
        job_scores = [
            score_candidate_for_job(candidate, job_id, job)
            for job_id, job in requirements["jobs"].items()
        ]
        job_scores.sort(key=lambda item: item["score"], reverse=True)
        ranked.append(
            {
                "candidate": candidate["candidate"],
                "resume_path": candidate["resume_path"],
                "best_job_id": job_scores[0]["job_id"],
                "best_role": job_scores[0]["role"],
                "best_score": job_scores[0]["score"],
                "scores": job_scores,
            }
        )
    ranked.sort(key=lambda item: item["best_score"], reverse=True)
    return ranked


def write_csv(rankings: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "rank",
        "candidate",
        "resume_path",
        "best_job_id",
        "best_role",
        "best_score",
        "score_32538",
        "score_32544",
        "score_30989",
        "matched_best_requirements",
        "missing_best_critical",
        "penalties",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rank, item in enumerate(rankings, start=1):
            score_by_job = {score["job_id"]: score for score in item["scores"]}
            best = item["scores"][0]
            writer.writerow(
                {
                    "rank": rank,
                    "candidate": item["candidate"],
                    "resume_path": item["resume_path"],
                    "best_job_id": item["best_job_id"],
                    "best_role": item["best_role"],
                    "best_score": item["best_score"],
                    "score_32538": score_by_job["32538"]["score"],
                    "score_32544": score_by_job["32544"]["score"],
                    "score_30989": score_by_job["30989"]["score"],
                    "matched_best_requirements": "; ".join(req["label"] for req in best["matched_requirements"][:8]),
                    "missing_best_critical": "; ".join(best["missing_critical"][:8]),
                    "penalties": "; ".join(penalty["label"] for penalty in best["penalties"]),
                }
            )


def validate(rankings: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not GROUND_TRUTH_PATH.exists():
        return None
    manifest = load_json(GROUND_TRUTH_PATH)
    role_to_job_id = {
        "ai_builder_senior_consultant": "32538",
        "ai_builder_manager": "32544",
        "data_ai_alliance_exec": "30989",
    }
    truth = {
        item["folder"]: {
            "target_job_id": role_to_job_id[item["target_role"]],
            "target_role": item["target_role"],
            "fit_tier": item["fit_tier"],
            "alignment_score": item["alignment_score"],
        }
        for item in manifest
    }
    matches = 0
    total = 0
    by_tier: dict[str, list[float]] = {}
    by_tier_accuracy: dict[str, dict[str, int]] = {}
    for item in rankings:
        expected = truth.get(item["candidate"])
        if not expected:
            continue
        total += 1
        is_match = item["best_job_id"] == expected["target_job_id"]
        matches += 1 if is_match else 0
        by_tier.setdefault(expected["fit_tier"], []).append(item["best_score"])
        stats = by_tier_accuracy.setdefault(expected["fit_tier"], {"matches": 0, "total": 0})
        stats["total"] += 1
        stats["matches"] += 1 if is_match else 0
    return {
        "top_1_job_accuracy": round(matches / total, 4) if total else None,
        "evaluated_candidates": total,
        "average_best_score_by_fit_tier": {
            tier: round(sum(scores) / len(scores), 2) for tier, scores in sorted(by_tier.items())
        },
        "top_1_accuracy_by_fit_tier": {
            tier: round(stats["matches"] / stats["total"], 4) for tier, stats in sorted(by_tier_accuracy.items())
        },
    }


def main() -> None:
    args = parse_args()
    requirements = load_json(args.requirements)
    signals = load_json(args.signals)
    rankings = rank_candidates(requirements, signals)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(rankings, indent=2) + "\n", encoding="utf-8")
    write_csv(rankings, args.csv_output)

    validation = validate(rankings)
    if validation:
        args.validation_output.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    print(f"Candidates ranked: {len(rankings)}")
    print(f"JSON output: {args.json_output}")
    print(f"CSV output: {args.csv_output}")
    if validation:
        print(f"Validation output: {args.validation_output}")
        print(f"Top-1 job accuracy: {validation['top_1_job_accuracy']}")


if __name__ == "__main__":
    main()
