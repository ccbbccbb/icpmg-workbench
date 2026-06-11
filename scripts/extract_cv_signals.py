# /// script
# dependencies = []
# ///

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REQUIREMENTS_PATH = ROOT / "job_descriptions" / "job_requirements.json"
OUTPUT_DIR = ROOT / "outputs"
DEFAULT_JSON_OUTPUT = OUTPUT_DIR / "cv_signal_extracts.json"
DEFAULT_CSV_OUTPUT = OUTPUT_DIR / "cv_signal_extracts.csv"
CURRENT_YEAR = 2026

SECTION_HEADINGS = {
    "PROFESSIONAL SUMMARY",
    "AREAS OF EXPERTISE",
    "AREAS OF EXPERIENCE",
    "CORE SKILLS",
    "PROFESSIONAL EXPERIENCE",
    "SELECTED ACHIEVEMENTS",
    "SELECTED PROJECTS",
    "AGENTIC AI BUILD LEADERSHIP",
    "AGENTIC AI BUILD PORTFOLIO",
    "REVENUE AND ALLIANCE IMPACT",
    "TOOLS, PLATFORMS, AND METHODS",
    "TOOLS AND METHODS",
    "CERTIFICATIONS",
    "EDUCATION",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract structured signals from existing candidate CV txt files.")
    parser.add_argument("--requirements", type=Path, default=REQUIREMENTS_PATH)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    return parser.parse_args()


def load_requirements(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_resumes() -> list[Path]:
    resumes: list[Path] = []
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or folder.name in {"synthetic_resumes", "job_descriptions", "outputs"}:
            continue
        txts = sorted(folder.glob("*_resume.txt"))
        if len(txts) == 1:
            resumes.append(txts[0])
    return resumes


def normalize(text: str) -> str:
    return text.lower().replace("&", " and ")


def term_pattern(term: str) -> re.Pattern[str]:
    normalized = normalize(term).strip()
    escaped = re.escape(normalized).replace("\\ ", r"\s+")
    prefix = r"(?<![a-z0-9])" if normalized and normalized[0].isalnum() else ""
    suffix = r"(?![a-z0-9])" if normalized and normalized[-1].isalnum() else ""
    return re.compile(prefix + escaped + suffix)


def snippets_for_term(text: str, term: str, limit: int = 2) -> list[str]:
    pattern = term_pattern(term)
    snippets: list[str] = []
    for line in text.splitlines():
        if not pattern.search(normalize(line)):
            continue
        snippet = re.sub(r"\s+", " ", line).strip()
        if len(snippet) > 220:
            snippet = snippet[:217].rstrip() + "..."
        snippets.append(snippet)
        if len(snippets) >= limit:
            break
    return snippets


def count_term(text: str, term: str) -> int:
    return len(term_pattern(term).findall(normalize(text)))


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"HEADER": []}
    current = "HEADER"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line in SECTION_HEADINGS:
            current = line
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw_line)
    return {key: "\n".join(value).strip() for key, value in sections.items() if "\n".join(value).strip()}


def parse_contact(text: str) -> dict[str, Any]:
    emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
    urls = sorted(set(re.findall(r"https?://[^\s)]+", text)))
    return {"emails": emails, "urls": urls}


def parse_experience(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    periods: list[dict[str, Any]] = []
    titles: list[str] = []
    companies: list[str] = []
    date_re = re.compile(r"^(20\d{2})\s+-\s+(20\d{2}|Present)$")

    for idx, line in enumerate(lines):
        match = date_re.match(line)
        if not match:
            continue
        start = int(match.group(1))
        end_raw = match.group(2)
        end = CURRENT_YEAR if end_raw == "Present" else int(end_raw)
        if end < start or start > CURRENT_YEAR:
            continue
        title_line = lines[idx - 1] if idx > 0 else ""
        title = title_line
        company = ""
        if " - " in title_line:
            title, company = title_line.split(" - ", 1)
        titles.append(title.strip())
        if company:
            companies.append(company.strip())
        periods.append({"title": title.strip(), "company": company.strip(), "start_year": start, "end_year": end, "end_label": end_raw, "years": end - start})

    total_years = sum(period["years"] for period in periods)
    return {
        "periods": periods,
        "total_experience_years": total_years,
        "titles": sorted(set(titles)),
        "companies": sorted(set(companies)),
    }


def parse_education_and_certs(sections: dict[str, str]) -> dict[str, list[str]]:
    education = [line.strip(" *-") for line in sections.get("EDUCATION", "").splitlines() if line.strip()]
    certifications = [line.strip(" *-") for line in sections.get("CERTIFICATIONS", "").splitlines() if line.strip()]
    return {"education": education, "certifications": certifications}


def requirement_hits(text: str, requirements: dict[str, Any]) -> dict[str, Any]:
    jobs: dict[str, Any] = {}
    for job_id, job in requirements["jobs"].items():
        matched_requirements = []
        for req in job["requirements"]:
            term_hits = []
            unique_terms = 0
            total_hits = 0
            for term in req["terms"]:
                hits = count_term(text, term)
                if hits:
                    unique_terms += 1
                    total_hits += hits
                    term_hits.append({"term": term, "count": hits, "snippets": snippets_for_term(text, term)})
            if term_hits:
                matched_requirements.append(
                    {
                        "id": req["id"],
                        "label": req["label"],
                        "priority": req["priority"],
                        "weight": req["weight"],
                        "min_hits": req.get("min_hits", 1),
                        "unique_terms": unique_terms,
                        "total_hits": total_hits,
                        "terms": term_hits,
                    }
                )
        jobs[job_id] = {
            "role": job["role"],
            "matched_requirements": matched_requirements,
            "matched_requirement_count": len(matched_requirements),
        }
    return jobs


def negative_hits(text: str, requirements: dict[str, Any]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for indicator in requirements.get("global_negative_indicators", []):
        terms = []
        for term in indicator["terms"]:
            count = count_term(text, term)
            if count:
                terms.append({"term": term, "count": count})
        if terms:
            hits.append({"id": indicator["id"], "label": indicator["label"], "penalty": indicator["penalty"], "terms": terms})
    return hits


def extract_resume(path: Path, requirements: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    contact = parse_contact(text)
    experience = parse_experience(text)
    education = parse_education_and_certs(sections)
    candidate = path.parent.name
    return {
        "candidate": candidate,
        "folder": path.parent.name,
        "resume_path": str(path.relative_to(ROOT)),
        "resume_file": path.name,
        "word_count": len(re.findall(r"\S+", text)),
        "sections_present": sorted(section for section in sections if section != "HEADER"),
        "contact": contact,
        "experience": experience,
        "education": education["education"],
        "certifications": education["certifications"],
        "job_requirement_hits": requirement_hits(text, requirements),
        "negative_indicators": negative_hits(text, requirements),
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "candidate",
        "resume_path",
        "word_count",
        "total_experience_years",
        "title_count",
        "url_count",
        "negative_indicator_count",
        "32538_matched_requirements",
        "32544_matched_requirements",
        "30989_matched_requirements",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "candidate": row["candidate"],
                    "resume_path": row["resume_path"],
                    "word_count": row["word_count"],
                    "total_experience_years": row["experience"]["total_experience_years"],
                    "title_count": len(row["experience"]["titles"]),
                    "url_count": len(row["contact"]["urls"]),
                    "negative_indicator_count": len(row["negative_indicators"]),
                    "32538_matched_requirements": row["job_requirement_hits"]["32538"]["matched_requirement_count"],
                    "32544_matched_requirements": row["job_requirement_hits"]["32544"]["matched_requirement_count"],
                    "30989_matched_requirements": row["job_requirement_hits"]["30989"]["matched_requirement_count"],
                }
            )


def main() -> None:
    args = parse_args()
    requirements = load_requirements(args.requirements)
    resumes = discover_resumes()
    rows = [extract_resume(path, requirements) for path in resumes]

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    write_csv(rows, args.csv_output)

    print(f"Resumes extracted: {len(rows)}")
    print(f"JSON output: {args.json_output}")
    print(f"CSV output: {args.csv_output}")


if __name__ == "__main__":
    main()
