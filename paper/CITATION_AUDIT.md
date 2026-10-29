# Citation and Similarity Audit

This document audits the matches identified in the Turnitin Similarity Report (12% overall similarity) and verifies attributions, sources, and literature context for the revision of `paper_revised.tex`.

---

## 1. Summary of Identified Similarity Matches

| Turnitin Match ID | Matched Text / Segment | Original Context in Paper | Source Identified in Turnitin | Audit & Revision Action |
|:---|:---|:---|:---|:---|
| **#15, #47** | "Coronary artery disease (CAD) involves atherosclerotic narrowing of the coronary arteries and is part of the broader burden of ischemic heart disease, a leading cause of death worldwide [2]." | Section I: Introduction | WHO reports / standard epidemiology surveys | **Restructure & Direct Framing:** Rephrase epidemiologic framing into direct clinical context regarding diagnostic decision-making without stock introductory boilerplate. |
| **#16, #42** | "Cleveland heart-disease dataset, with attention to outcome coding and the joint treatment of measurements and symptom categories. Four continuous variables were modeled with Gaussian likelihoods; chest-pain type and exercise-induced angina were modeled with Laplace-smoothed categorical likelihoods." | Abstract & Section IV | Student papers / UCI dataset reports | **Disentangle & Re-order:** State specific modeling architecture directly; lead with the exact hybrid likelihood construction rather than standard dataset overview phrasing. |
| **#26, #15** | "Detrano et al. developed a probability-based diagnostic rule... The Cleveland records later became a widely used benchmark distributed through the UCI Machine Learning Repository [1]... the original five-level outcome is collapsed to a binary label for this experiment." | Section III: Literature Review | Detrano et al. (1989), UCI Repository documentation | **Clarify Attribution:** State clearly that Detrano et al. originally used a probabilistic decision rule across four sites, whereas subsequent machine-learning literature narrowed focus to Cleveland and collapsed the 5-point scale to a binary cut. |
| **#28, #22** | "Naive Bayes assumes that features are conditionally independent given the class, an assumption that is rarely exact in clinical data... while the Brier score provides a proper scoring rule for probabilistic predictions [9], [10]." | Section III & Section V | Domingos & Pazzani (1997), Rish (2001), Brier (1950) | **Tighten Mathematical Prose:** Eliminate filler transitions. Distinguish zero-one classification loss ranking from quadratic scoring of posterior probabilities directly. |
| **#20, #41, #18, #44, #46** | "Khanna et al. evaluated support-vector machines, logistic regression, and neural networks... Amin et al. compared seven methods... Akella and Akella assessed six machine-learning methods... Meidina and Abidin studied Naive Bayes with PSO..." | Section III: Literature Review | Survey of Cleveland ML benchmarks | **Synthesize by Methodological Theme:** Instead of a monotonous serial list of "Author X compared Y methods using Z", synthesize them thematically around their reliance on ad-hoc discretization or unverified data splits. |
| **#30, #29, #38** | "The repository documented by UCI contains four heart-disease databases assembled by Robert Detrano... less than 50% diameter narrowing and values 1 through 4 as more than 50% narrowing in a major vessel." | Section IV-A: Dataset Provenance | Aha (1988) UCI documentation, Detrano (1989) | **Standard Technical Definitions:** Directly quote specific threshold text from documentation where required (`"less than 50% diameter narrowing"`) or state the mathematical threshold formula $C = \mathbb{I}(\text{num} > 0)$ cleanly. |
| **#35, #16** | Feature definitions: "Resting blood pressure (trestbps, mm Hg): admission arterial pressure. Serum cholesterol (chol, mg/dl): fasting lipid profile. Maximum heart rate (thalach, beats/min)... Exercise-induced angina (exang)..." | Section IV-B: Feature Selection | UCI Heart Disease attribute dictionary | **Tabular Integration:** Present attribute clinical semantics concisely in the table; streamline running prose. |
| **#33, #40, #45** | Likelihood and smoothing formulas: "Naive Bayes approximation treats predictors as independent once the class is known... $\prod_{j=1}^d P(x_j \mid C=c)$... $\log S(c \mid \mathbf{x}) = \log P(C=c) + \dots$" | Section V: Mathematical Foundations | Standard Bayesian pattern recognition textbooks (Bishop 2006) | **Mathematical Identity:** Formulas are standard mathematics; trim redundant explanatory scaffolding around textbook equations. |
| **#19, #24, #1, #12** | Methodology & Validation: "Within each fold, the class priors... estimated from training records only... fitted on the training data and then applied to the test data... repeated stratified $10 \times 5$-fold cross-validation..." | Section VI: Methodology | Standard ML methodology phrasing | **Direct Procedural Narration:** Describe pipeline mechanics strictly chronologically and operationally without boilerplate textbook descriptions of cross-validation. |
| **#11, #8, #49** | Metrics definitions: Accuracy, Precision, Recall, Specificity, F1, ROC-AUC, Brier score. | Section VI-D: Metrics | Standard definition formulas | **Compact Presentation:** Group metric formulas compactly; remove generic textbook definitions of TP/FP/TN/FN. |
| **#1, #2, #3, #6, #14, #21, #32** | Reproducibility Statement: "The analyses were run in Python 3.10 using NumPy, pandas, SciPy, scikit-learn, and Matplotlib... Random seeds were 42..." | Section X / Back matter | Standard software environment phrasing | **Concise Operational Instructions:** State software dependencies and exact command-line execution cleanly and succinctly. |

---

## 2. Attributions and Citations Verified

- **[1] UCI Repository**: Janosi, Steinbrunn, Pfisterer, Detrano (1989). Valid canonical dataset citation.
- **[2] WHO**: Global health mortality statistics. Valid general epidemiology context.
- **[3] AHA**: Invasive angiography risks and context.
- **[4] Detrano et al. (1989)**: Original paper describing the multicenter probabilistic algorithm (Cleveland, Hungary, Zurich, Long Beach).
- **[5] Domingos & Pazzani (1997)**: Key theorem on 0-1 loss optimality of Naive Bayes under violated independence.
- **[6] Rish (2001)**: Empirical study explaining why Naive Bayes works well for classification despite poor probabilities.
- **[7] Scikit-learn (Pedregosa et al., 2011)**: Machine learning toolkit used for baseline models and evaluation harness.
- **[8] Fawcett (2006)**: Standard ROC analysis primer.
- **[9] Brier (1950)**: Original strictly proper scoring rule paper.
- **[10] Niculescu-Mizil & Caruana (2005)**: Calibration behavior across supervised learners (ICML).
- **[11] Aha (1988)**: Original UCI documentation note regarding `cleveland.data` vs `processed.cleveland.data`.
- **[12] Bishop (2006)**: Pattern Recognition and Machine Learning reference.
- **[13] Khanna et al. (2015)**: Benchmark comparison on Cleveland.
- **[14] Amin et al. (2019)**: Telematics and Informatics feature selection / classification on Cleveland.
- **[15] Akella & Akella (2021)**: Open source ML algorithms on CAD.
- **[16] Meidina & Abidin (2023)**: Naive Bayes optimization on Cleveland.

