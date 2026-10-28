"""Mixed Gaussian/categorical Naive Bayes used in the CAD paper."""
from __future__ import annotations

import math
import time
from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
import pandas as pd

NUMERIC = ("age", "trestbps", "chol", "thalach")
CATEGORICAL = ("cp", "exang")
CATEGORY_SETS = {"cp": (1, 2, 3, 4), "exang": (0, 1)}
NUMERIC_BOUNDS = {"age": (20, 100), "trestbps": (80, 220), "chol": (100, 600), "thalach": (60, 220)}

@dataclass
class Prediction:
    probability: float
    log_scores: dict[int, float]
    contributions: dict[str, float]
    inference_ms: float

class MixedNaiveBayes:
    def __init__(self, alpha: float = 1.0, variance_floor: float = 1e-6):
        self.alpha, self.variance_floor = float(alpha), float(variance_floor)

    def fit(self, frame: pd.DataFrame, target: str = "target") -> MixedNaiveBayes:
        started = time.perf_counter(); y = (frame[target].to_numpy() > 0).astype(int)
        self.n_records = int(len(frame)); self.counts = {c: int((y == c).sum()) for c in (0, 1)}
        self.log_prior = {c: math.log(self.counts[c] / self.n_records) for c in (0, 1)}
        self.means, self.variances = {0:{},1:{}}, {0:{},1:{}}
        self.cat_counts, self.cat_log_probs = {0:{},1:{}}, {0:{},1:{}}
        for c in (0, 1):
            group = frame.loc[y == c]
            for feature in NUMERIC:
                self.means[c][feature] = float(group[feature].mean())
                self.variances[c][feature] = max(float(group[feature].var(ddof=0)), self.variance_floor)
            for feature, levels in CATEGORY_SETS.items():
                counts = {level: int((group[feature] == level).sum()) for level in levels}
                den = self.counts[c] + self.alpha * len(levels)
                self.cat_counts[c][feature] = counts
                self.cat_log_probs[c][feature] = {level: math.log((n+self.alpha)/den) for level,n in counts.items()}
        self.fit_seconds = time.perf_counter() - started
        return self

    @staticmethod
    def validate_inputs(values: Mapping[str, float | int]) -> dict[str, float | int]:
        bounds = NUMERIC_BOUNDS; out={}
        for feature, (lo, hi) in bounds.items():
            value=float(values[feature])
            if not lo <= value <= hi: raise ValueError(f"{feature} must be between {lo} and {hi}.")
            out[feature]=value
        for feature, allowed in CATEGORY_SETS.items():
            value=int(values[feature])
            if value not in allowed: raise ValueError(f"{feature} must be one of {allowed}.")
            out[feature]=value
        return out

    def feature_log_terms(self, values: Mapping[str, float | int], c: int) -> dict[str, float]:
        v=self.validate_inputs(values); terms={}
        for f in NUMERIC:
            var, mean=self.variances[c][f], self.means[c][f]
            terms[f] = -0.5*math.log(2*math.pi*var) - (float(v[f])-mean)**2/(2*var)
        for f in CATEGORICAL: terms[f] = self.cat_log_probs[c][f][int(v[f])]
        return terms

    def predict_one(self, values: Mapping[str, float | int]) -> Prediction:
        started=time.perf_counter(); v=self.validate_inputs(values); terms={c:self.feature_log_terms(v,c) for c in (0,1)}
        scores={c:self.log_prior[c]+sum(terms[c].values()) for c in (0,1)}; top=max(scores.values())
        shifted={c:math.exp(scores[c]-top) for c in (0,1)}; prob=shifted[1]/sum(shifted.values())
        contrib={f:terms[1][f]-terms[0][f] for f in NUMERIC+CATEGORICAL}
        return Prediction(prob, scores, contrib, (time.perf_counter()-started)*1000)

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        n = len(frame); scores = np.empty((n, 2))
        for c in (0, 1):
            total = np.full(n, self.log_prior[c])
            for f in NUMERIC:
                var, mean = self.variances[c][f], self.means[c][f]
                x = frame[f].to_numpy(dtype=float)
                total += -0.5 * np.log(2 * np.pi * var) - (x - mean) ** 2 / (2 * var)
            for f in CATEGORICAL:
                total += frame[f].astype(int).map(self.cat_log_probs[c][f]).to_numpy(dtype=float)
            scores[:, c] = total
        with np.errstate(over="ignore"):
            p1 = 1.0 / (1.0 + np.exp(scores[:, 0] - scores[:, 1]))
        return np.column_stack([1 - p1, p1])
