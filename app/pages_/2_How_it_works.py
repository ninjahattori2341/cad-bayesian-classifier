"""Readable mathematical walkthrough for the live model calculation."""
from trace import render_trace

import streamlit as st
from common import load_model, page_intro, values
from paths import DATA_CSV

model = load_model()
current = values()
theta = float(st.session_state.get("theta", 0.50))
prediction = model.predict_one(current)
page_intro(
    "METHOD",
    "How it works",
    "A guided calculation walkthrough for the current inputs. The notation below mirrors the implementation.",
)
st.markdown(
    '<nav class="stepper" aria-label="Calculation steps">'
    + " ".join(f'<a href="#step-{i}">{i}</a>' for i in range(1, 8))
    + "</nav>",
    unsafe_allow_html=True,
)
st.caption("Notation: (C=0) is the recorded control class, (C=1) is the recorded CAD-positive class, and (x) is the six-field input vector.")

steps = [
    (
        "Start from the class prior",
        r"\pi_c = P(C=c) = \frac{N_c}{N}, \qquad c\in\{0,1\}",
        f"The fitted cohort contains {model.counts[0]} control records and {model.counts[1]} CAD-positive records out of {model.n_records}.",
    ),
    (
        "Score each numeric feature",
        r"\log p(x_j\mid C=c) = -\frac{1}{2}\log(2\pi\sigma^2_{jc}) - \frac{(x_j-\mu_{jc})^2}{2\sigma^2_{jc}}",
        "Each measurement is compared with the class-conditional Gaussian estimated from the training cohort.",
    ),
    (
        "Score each categorical feature",
        r"p(x_j=v\mid C=c) = \frac{n_{jcv}+\alpha}{N_c+\alpha\,|\mathcal K_j|}, \qquad \alpha=1",
        "Chest-pain and exercise-pain levels use Laplace smoothing so every allowed level receives a finite likelihood.",
    ),
    (
        "Add the evidence in log space",
        r"s_c(x) = \log\pi_c + \sum_{j\in\mathcal N}\log p(x_j\mid C=c) + \sum_{j\in\mathcal K}\log p(x_j\mid C=c)",
        f"The current log-scores are (s_0={prediction.log_scores[0]:.3f}) and (s_1={prediction.log_scores[1]:.3f}).",
    ),
    (
        "Normalise with log-sum-exp",
        r"P(C=1\mid x) = \frac{\exp(s_1-M)}{\exp(s_0-M)+\exp(s_1-M)}, \qquad M=\max(s_0,s_1)",
        f"Subtracting (M) improves numerical stability without changing the resulting probability: (P(C=1\\mid x)={prediction.probability:.6f}).",
    ),
    (
        "Apply the decision threshold",
        r"\widehat C_\theta(x) = \begin{cases}1,&P(C=1\mid x)\geq\theta\\0,&P(C=1\mid x)<\theta\end{cases}",
        f"The current threshold is \\(\\theta={theta:.2f}\\). It changes only the displayed class label, not the posterior probability.",
    ),
    (
        "Cross-check the arithmetic",
        r"\Delta = \left|P_{\mathrm{mixed\ NB}}(C=1\mid x)-P_{\mathrm{sklearn}}(C=1\mid x)\right|",
        "The trace below compares this implementation with independent GaussianNB and CategoricalNB components.",
    ),
]
for index, (title, equation, gloss) in enumerate(steps, 1):
    with st.container(border=True):
        st.markdown(f'<div id="step-{index}"></div>', unsafe_allow_html=True)
        st.markdown(f"### {index}. {title}")
        st.latex(equation)
        st.write(gloss)

st.divider()
st.markdown("### Live trace and cross-check")
render_trace(model, current, theta, DATA_CSV)
