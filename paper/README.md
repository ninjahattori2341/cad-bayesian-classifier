# CAD Bayesian Classification Project

This project studies retrospective binary classification on the processed UCI Cleveland heart-disease dataset. It compares a mixed Gaussian-categorical Naive Bayes classifier with numeric-only Gaussian Naive Bayes and regularized logistic regression. The model output is an experimental classification result, not a clinical diagnosis or a future-risk estimate.

## Files

- `heart_cleveland_clean.csv` — cleaned Cleveland records used by the experiment.
- `experiments.py` — training, validation, metrics, and figure-generation script.
- `results.json` — saved summary of the experiment.
- `figs/` — generated figures included by `paper.tex`.
- `paper.tex` — IEEE-style LaTeX report source.
- `paper.pdf` — compiled report.

## Requirements

- Python 3.10 or compatible.
- Python packages: NumPy, pandas, SciPy, scikit-learn, and Matplotlib.
- Tectonic or another LaTeX installation with IEEEtran available to compile the report.

Install the Python dependencies with:

```powershell
python -m pip install numpy pandas scipy scikit-learn matplotlib
```

## Run the experiment

From this project directory, run:

```powershell
python experiments.py
```

The script reads `heart_cleveland_clean.csv`, writes `results.json`, and regenerates the plots under `figs/`. The seeded holdout and repeated cross-validation runs are specified in the script. Review the saved results against the reported values before submitting the report.

## Compile the report

With Tectonic installed, run:

```powershell
tectonic paper.tex
```

Alternatively, use the bundled Tectonic executable on Windows:

```powershell
.\tools\tectonic.exe paper.tex
```

## Data and interpretation

The data originate from the UCI Heart Disease collection, Cleveland Clinic Foundation subset. The binary target is `0` for recorded `num=0` and `1` for recorded `num>0`. The analysis uses six predictors: `age`, `trestbps`, `chol`, `thalach`, `cp`, and `exang`. Read the report's limitations before interpreting the results; this historical, single-site dataset does not establish present-day clinical performance.

## Academic use

The report and code should be reviewed and understood by the project author. Be prepared to explain the target coding, model assumptions, validation design, metrics, results, and limitations during the viva. Follow the instructor's rules for acknowledging assistance and maintaining academic integrity.

## Submission-format note

The revised source of truth is `paper.tex`, and its current IEEE-style compiled report is `paper.pdf` (8 pages). The course brief mentions a Microsoft Word IEEE template. The existing `Final_CAD_Bayesian_Classification_Paper.docx` and matching PDF are older drafts and do not reflect the revisions in `paper.tex`; do not submit those older files as if they were current. The instructor's actual Word template was not present in this project folder when this revision was made.
