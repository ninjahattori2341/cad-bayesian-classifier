# Author Review & Verification Log

This document records technical points, phrasing decisions, and items flagged for author confirmation during the revision of `paper_revised.tex`.

---

## 1. Verified Points Against Code and `results.json`

- **Record Retention & Duplicate Check:**
  - Total rows in `heart_cleveland_clean.csv`: **303**.
  - A duplicate check on all 13 predictor columns yields **0** duplicates.
  - A duplicate check on the 6 selected features yields **0** duplicates.
  - Phrasing in `paper_revised.tex` explicitly states that auditing the full 13 predictor fields confirmed that every one of the 303 rows corresponds to a distinct record, retaining the complete sample without ad-hoc row removal.

- **Outcome Labels & Counts:**
  - Controls ($C=0$, $\text{num}=0$): **164** ($54.12\%$).
  - CAD-present ($C=1$, $\text{num} \ge 1$): **139** ($45.88\%$).
  - Target encoding verified against Dr. Detrano's documentation: $\text{num}=0$ means $<50\%$ stenosis, $\text{num} \ge 1$ means $\ge 50\%$ diameter narrowing in at least one major vessel.

- **Exact Numerical Match Verification:**
  - **Holdout (80/20, $N=61$, 33 controls, 28 CAD):**
    - Mixed NB: Accuracy $80.3\%$, Recall $82.1\%$, Specificity $78.8\%$, Precision $76.7\%$, F1 $0.793$, ROC-AUC $0.891$, Brier score $0.142$, TP=23, FP=7, FN=5, TN=26.
    - Bootstrap 95% CIs: Accuracy $[70.5\%, 90.2\%]$, ROC-AUC $[0.803, 0.960]$.
    - Logistic Regression: Accuracy $82.0\%$, Recall $78.6\%$, Specificity $84.8\%$, Precision $81.5\%$, F1 $0.800$, ROC-AUC $0.898$, Brier score $0.126$, TP=22, FP=5, FN=6, TN=28.
    - Gaussian NB (numeric): Accuracy $72.1\%$, Recall $64.3\%$, Specificity $78.8\%$, Precision $72.0\%$, F1 $0.679$, ROC-AUC $0.765$, Brier score $0.202$.
    - Decision Tree (fixed): Accuracy $75.4\%$, Recall $60.7\%$, Specificity $87.9\%$, Precision $81.0\%$, F1 $0.694$, ROC-AUC $0.860$, Brier score $0.146$.
  - **Repeated CV ($10 \times 5$-fold, 50 folds):**
    - Mixed NB: Accuracy $0.748 \pm 0.048$, Precision $0.733 \pm 0.064$, Recall $0.714 \pm 0.073$, Specificity $0.776 \pm 0.070$, F1 $0.721 \pm 0.055$, ROC-AUC $0.831 \pm 0.045$, Brier score $0.183 \pm 0.032$.
    - Gaussian NB (numeric): Accuracy $0.677 \pm 0.050$, Recall $0.607 \pm 0.082$, ROC-AUC $0.732 \pm 0.052$, Brier score $0.218 \pm 0.027$.
    - Logistic Regression: Accuracy $0.751 \pm 0.050$, Precision $0.743 \pm 0.072$, Recall $0.707 \pm 0.077$, Specificity $0.788 \pm 0.073$, F1 $0.722 \pm 0.058$, ROC-AUC $0.830 \pm 0.049$, Brier score $0.168 \pm 0.026$.
    - Paired AUC Difference (Mixed NB vs LR): $+0.0011 \pm 0.0188$, exploratory paired-fold Wilcoxon $p = 0.652$.
    - Symptom ablation gain: $+0.099$ in mean CV AUC ($0.831$ vs $0.732$).
  - **Within-Class Diagnostics:**
    - Age vs `thalach` correlation in controls: $r = -0.523$.
    - Cholesterol skewness in controls: $\text{skew} = 1.13$.
    - Shapiro-Wilk $p$-values: resting BP in CAD ($p = 1.17 \times 10^{-4}$), cholesterol in controls ($p = 2.88 \times 10^{-9}$), `thalach` in controls ($p = 5.43 \times 10^{-4}$).

---

## 2. Items Flagged for Author Review

1. **Section III (Literature Review synthesis):**
   - *Original phrasing:* Listed Khanna et al., Amin et al., Akella & Akella, and Meidina & Abidin serially with repetitive sentences ("X evaluated...", "Y compared...").
   - *Revision:* Synthesized into two methodological clusters: (1) studies evaluating discriminative algorithms (SVMs, trees, neural networks) on Cleveland, and (2) studies specifically tuning Naive Bayes or feature subsets. Please confirm that this synthesis accurately reflects your literature scope.

2. **Section IV-A (Duplicate handling description):**
   - Phrased strictly as an audit finding without speculating on specific library methods (e.g. `pandas.drop_duplicates()`): "Because preliminary processing scripts in benchmark studies often drop duplicate rows based on subset keys, we audited all 13 predictor columns in `processed.cleveland.data` and verified that each of the 303 rows represents an individual patient record." Please verify this fits your recollection.

3. **Section IV-B (Six-feature selection rationale):**
   - Phrased to highlight both the conceptual design (evaluating mixed continuous/categorical likelihoods in Naive Bayes) and the clean data availability (avoiding missing data imputation for `ca` and `thal`): "We selected six attributes to study how continuous physiological measurements and discrete clinical symptoms interact within a hybrid Bayesian likelihood structure without introducing synthetic imputation."

