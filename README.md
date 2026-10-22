# CardioRisk

### A research companion for mixed-type Bayesian classification

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-147d78.svg)](LICENSE)

CardioRisk pairs an eight-page research paper with a runnable implementation of a mixed Gaussian and categorical Naive Bayes classifier. It is designed to make the work inspectable: readers can explore the model, follow its arithmetic for a hypothetical input, examine the cleaned cohort, and review the paper's saved evaluation results.

**This is an educational research demonstration—not a medical device, diagnostic tool, or source of care advice.** It classifies a historical diagnosis recorded at examination; it does not estimate future disease risk. The model was developed from 303 records from a single site and era. Its probabilities were less well calibrated than logistic regression in the paper's repeated cross-validation (Brier score 0.183 vs 0.168). Do not use the app for clinical decisions.

| Explore | Read | Run |
| --- | --- | --- |
| [Open the hosted CardioRisk app](https://cad-bayesian-classifier-du6waxa8visd2llvxlegss.streamlit.app/) | [Read the paper PDF](paper/paper.pdf) · [View its LaTeX source](paper/paper.tex) | [Install and launch locally](#run-the-app) |

> If the hosted app asks you to sign in, the deployment owner may need to adjust its Streamlit sharing settings. The code and research materials are available in this repository either way.

## What this project studies

The paper evaluates whether a transparent Naive Bayes model can combine continuous measurements and categorical symptom fields in the UCI Cleveland heart-disease dataset. Its target is `target = (num > 0)`: the recorded diagnosis is collapsed to control (`0`) or CAD-positive (`1`). This is retrospective classification of the diagnosis in the record—not prediction of a future event.

The implementation uses six predictors:

| Type | Fields | Model treatment |
| --- | --- | --- |
| Continuous | `age`, `trestbps`, `chol`, `thalach` | Class-conditional Gaussian likelihoods; maximum-likelihood variance (`ddof=0`) with a `1e-6` floor |
| Categorical | `cp` (levels 1–4), `exang` (levels 0–1) | Class-conditional frequencies with Laplace smoothing (`alpha=1`) |

The class scores are summed in log space and normalized with log-sum-exp. A selectable threshold changes the predicted class label, not the calculated posterior probability. Per-feature log-odds contributions show how each modeled input changes the score difference; they are an explanation of model arithmetic, not clinical reasoning.

## Research snapshot

The table below summarizes the saved 10-repeat, 5-fold stratified cross-validation results (50 folds) in [`paper/results.json`](paper/results.json). Values are mean ± fold standard deviation. AUC describes discrimination; Brier score summarizes probability error, where lower is better. See the paper for the full validation design, holdout analysis, confidence intervals, assumption checks, and limitations.

| Model | ROC-AUC | Brier score |
| --- | ---: | ---: |
| Mixed Gaussian + categorical NB | 0.831 ± 0.045 | 0.183 ± 0.032 |
| Gaussian NB (numeric features) | 0.732 ± 0.052 | 0.218 ± 0.027 |
| Logistic regression | 0.830 ± 0.049 | 0.168 ± 0.026 |
| Decision tree (fixed settings) | 0.808 ± 0.050 | 0.180 ± 0.028 |

These are results on a small, historical benchmark cohort. They are not evidence of clinical utility or generalization to current populations. In particular, the mixed model's weaker Brier score means its probability estimates were less calibrated than logistic regression's in this evaluation.

## Explore the app

- **Predict:** adjust the six inputs and decision threshold; inspect the posterior, model class, and feature log-odds contributions.
- **Stats for nerds:** expand the calculation trace for priors, Gaussian estimates, smoothed categorical likelihoods, class scores, posterior normalization, threshold comparison, runtime details, and an independent scikit-learn cross-check. Download the trace as JSON.
- **Data & Results:** explore the class balance, categorical distributions, fitted Gaussian curves, within-class correlations, saved cross-validation metrics, threshold sweep, and filterable records.
- **About:** review data provenance, method assumptions, limitations, and the paper's AI-assistance disclosure.

The app supports light and dark appearance modes. The cleaned CSV and results JSON are loaded from the repository's relative `paper/` directory, so a clone does not depend on a developer-specific path.

## Repository map

```text
cad_app/
├── app/
│   ├── streamlit_app.py       # Streamlit pages, app state, and UI
│   ├── nb_model.py            # Mixed Gaussian/categorical Naive Bayes
│   ├── trace.py               # Step-by-step arithmetic and JSON export
│   ├── viz.py                 # Interactive Plotly chart builders
│   └── style.css              # Light/dark design system and responsive styling
├── paper/
│   ├── paper.pdf              # Compiled, anonymous research paper
│   ├── paper.tex              # Paper source
│   ├── heart_cleveland_clean.csv # Cleaned 303-record dataset used in the study
│   ├── results.json           # Saved experiment outputs used by the app
│   ├── experiments.py         # Reproducible evaluation and figure generation
│   ├── generate_paper.py      # Legacy Word export helper; not the current paper build
│   └── figs/                  # Figures included by the paper source
├── tests/test_model.py        # Model count, trace, and independent-check tests
├── .streamlit/config.toml     # Default Streamlit theme and server settings
├── requirements.txt           # App and experiment dependencies
├── requirements-dev.txt       # Test tooling
├── LICENSE
└── README.md
```

The supplied `paper_team13.pdf` was checked against `paper/paper.pdf`; they are identical, so the repository keeps one canonical PDF instead of a confusing duplicate. The current paper bundle includes both the compiled PDF and editable LaTeX source, all seven source figures, the cleaned dataset, saved results, and the experiment script. `paper/generate_paper.py` is an older Word-export helper, not part of the current PDF or experiment reproduction workflow.

## Run the app

Use Python 3.10 or newer. From the repository root, create and activate a virtual environment, then install the app dependencies:

**Windows PowerShell**

```powershell
python -m venv "$env:USERPROFILE\venvs\cad_app"
& "$env:USERPROFILE\venvs\cad_app\Scripts\Activate.ps1"
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Streamlit prints the local URL, normally `http://localhost:8501`. On Windows, keeping the virtual environment outside a OneDrive-synced project directory can reduce sync overhead. The Windows example does this by default.

## Deploy a copy on Streamlit Community Cloud

The repository is self-contained, so the deployed app does not need a local dataset path or secret. In Streamlit Community Cloud, create a new app from this GitHub repository, choose the `main` branch, and set the app entry point to `app/streamlit_app.py`. The root `requirements.txt` supplies the runtime and experiment packages. Cloud sharing settings determine whether visitors can open the app without signing in; test the published link in a private browser window before sharing it with a class or reviewer.

## Run the tests

Install the development test dependency and run the suite from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_model.py -q
```

The tests verify the expected class counts (164 controls / 139 CAD-positive), that feature contributions reconcile to the final log-odds, and that posteriors agree with an independent scikit-learn GaussianNB + CategoricalNB calculation on ten records within `1e-6`.

## Reproduce the paper's experiment outputs

The experiment script uses the processed CSV, writes `results.json`, and regenerates the figures under `paper/figs/`. These commands overwrite those generated outputs, so use a clean clone or a separate working branch if you want to preserve the checked-in snapshot unchanged.

```bash
cd paper
python experiments.py
```

The paper source is `paper/paper.tex`; its compiled companion is `paper/paper.pdf`. The experiment script does not compile the paper. To rebuild the PDF, use a LaTeX distribution that provides `IEEEtran.cls` and the packages required by the source, then run from `paper/`:

```bash
tectonic paper.tex
```

## Data provenance and responsible use

The cohort is the Cleveland Clinic Foundation subset of the [UCI Heart Disease dataset](https://doi.org/10.24432/C52P4X). The paper documents the processed-file choice, target encoding, duplicate checks, and evaluation procedure. Please cite UCI and consult the paper before reusing the data or interpreting its results.

Important limitations include the small sample, historical single-site collection, retrospective target, imperfect Gaussian fits, conditional dependence among predictors, and weaker probability calibration than logistic regression. The data do not establish current clinical performance. The displayed estimate and trace describe how this specific model behaves on supplied inputs; they do not tell a person whether they have a disease or what care to seek.

## AI-assistance disclosure

Generative AI tools were used as learning and editorial assistants to explain statistical concepts, revise manuscript wording and organization, review consistency between the report and project code, and suggest citation checks. The reported numerical results were generated by the documented Python pipeline; AI suggestions were not treated as evidence or as a substitute for cited sources. The author is responsible for verifying the data, code, calculations, references, and interpretations, and for understanding and explaining the work.

## License

The project code is distributed under the [MIT License](LICENSE). The dataset remains attributed to its [UCI source](https://doi.org/10.24432/C52P4X); check the source terms when redistributing the data separately.
