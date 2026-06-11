# Scripts

These scripts created and processed the synthetic candidate dataset used by the workbench. Run them with `uv run --script` when re-generating data. They were moved from the original dataset build folder, so pass explicit input/output paths if the source manifests, job requirements, or intermediate outputs are not colocated with the script defaults.

## Pipeline Order

```text
synth-cv.py
-> expand-existing-resumes.py
-> extract_cv_signals.py
-> rank_candidates.py
-> export_candidate_snapshots.py
```

## Script Index

* `synth-cv.py` creates the first-pass Faker resume set with synthetic candidate names, contact details, education, skills, and work history.
* `expand-existing-resumes.py` rewrites the existing candidate `.txt` resumes into richer CVs aligned to the three KPMG roles, with an intentionally uneven distribution of strong, review, partial, and weak-fit candidates. It also creates the role assignment manifest used for validation.
* `extract_cv_signals.py` reads candidate resume text and extracts structured signals against the job requirement taxonomy, including matched terms, evidence snippets, experience, titles, education, portfolio mentions, and weak-fit indicators.
* `rank_candidates.py` scores extracted CV signals against the three job descriptions, applies seniority and risk calibration, writes ranked outputs, and produces validation metrics against the synthetic assignment manifest.
* `export_candidate_snapshots.py` converts the heavier ranking output into the compact JSON payload consumed by the Next.js workbench UI.

## Main Artifacts

* Source resumes and profile images are served by the app from `public/candidates/`.
* The UI-facing payload is `data/workbench_candidate_snapshots.json`.
* The heavier extraction, ranking, and validation outputs are intermediate pipeline artifacts and are not loaded directly by the UI.
