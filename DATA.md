# Data: CV & Resume Volume -> Faster Candidate Selection

The data is structured to support the main thesis: high-volume screening is not just a resume-reading problem:

It is a workflow, evidence, fairness, + decision-support problem.

It does not treat a resume as a single blob of text, or a candidate as a single score.

Rather - it separates validation into source data, extracted evidence, ranking logic, reviewer-facing highlights, and auditability.

This is a win for everyone.

## Source Data

* **Job descriptions:** three KPMG postings are saved as source-of-truth text files before scoring.
* **Structured requirements:** each job is mapped into weighted criteria such as critical, strong, and supporting signals.
* **Candidate CVs:** 310 synthetic candidate folders contain one resume and one profile image each.
* **Ground truth for validation:** synthetic role/fit labels are kept separately from the UI-facing data so scoring can be tested without showing hidden labels to reviewers.

## Job-To-Candidate Distribution

```text
32538 -> AI Builder - Senior Consultant -> 175 candidates
32544 -> AI Builder - Manager            -> 93 candidates
30989 -> Data & AI Alliance Executive    -> 42 candidates
```

## Candidate Folder Mapping

```text
candidate_slug/
  candidate_slug_profile.png
  candidate_slug_resume.txt
```

Example:

```text
kevin_pace/
  kevin_pace_profile.png
  kevin_pace_resume.txt
```

The generated app snapshot maps that into:

```json
{
  "candidateId": "kevin_pace",
  "candidateName": "Kevin Pace",
  "profileImagePath": "kevin_pace/kevin_pace_profile.png",
  "resumePath": "kevin_pace/kevin_pace_resume.txt",
  "score": 95.32,
  "reviewBand": "Strong match",
  "highlights": ["Hands-on agentic AI building"],
  "missingCritical": [],
  "riskFlags": []
}
```

## Processing Pipeline

```text
raw job descriptions
-> structured job requirements
-> CV signal extraction
-> role-specific scoring
-> candidate snapshot export
-> reviewer workbench UI
```

## Generated Data Artifacts

* `data/workbench_candidate_snapshots.json` is the app-facing payload.
* Candidate images and resume text files live under `public/candidates/`.
* The heavier extraction and ranking outputs stay outside the UI bundle and are used for audit/tuning.

## Workbench Mapping

The workbench uses this mapping to show:

* **Evidence highlights:** why a candidate matched a requirement.
* **Missing signals:** critical or strong criteria not found in the CV.
* **Risk flags:** weak-fit indicators such as limited AI ownership or unrelated background.
* **Cross-role recommendations:** cases where a candidate appears stronger for another requisition.
* **Score comparison:** the candidate's fit across all three roles, not only the applied role.

The fairness goal is not to hide judgment behind automation. It is to make the review process more consistent and inspectable: the reviewer can see the evidence, gaps, and assumptions before deciding whether to shortlist, interview, or reject.
