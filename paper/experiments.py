import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_auc_score, brier_score_loss, f1_score,
    confusion_matrix, roc_curve
)
from sklearn.calibration import calibration_curve

# Styling for academic IEEE figures
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 300
})

os.makedirs('figs', exist_ok=True)

# 1. Load Data
# We use the verified authentic UCI Cleveland dataset
d = pd.read_csv('heart_cleveland_clean.csv')

# Ensure target is binary: 0 = no disease, 1 = angiographic disease (>50% narrowing)
d['C'] = d['target'].astype(int)

NUM = ['age', 'trestbps', 'chol', 'thalach']
CAT = ['cp', 'exang']

# Define fixed category sets K from domain knowledge to prevent leakage and handle unseen categories
CATEGORY_SETS = {
    'cp': [1.0, 2.0, 3.0, 4.0],
    'exang': [0.0, 1.0]
}

class MixedNB:
    """
    Mixed Naive Bayes Classifier combining:
    - Gaussian likelihoods with Maximum Likelihood variance (1/n) and variance floor for continuous features
    - Categorical likelihoods with Laplace (add-alpha) smoothing over known category domains
    """
    def __init__(self, alpha=1.0, floor=1e-6, category_sets=None):
        self.alpha = float(alpha)
        self.floor = float(floor)
        self.category_sets = category_sets or CATEGORY_SETS
        self.classes_ = np.array([0, 1])
        
    def fit(self, X, y):
        self.classes_ = np.unique(y)
        n_samples = len(y)
        # Class log-priors log P(C = c)
        self.log_prior_ = np.array([np.log(np.sum(y == c) / n_samples) for c in self.classes_])
        
        self.mu_ = {}
        self.var_ = {}
        self.cat_log_probs_ = {}
        self.cat_unseen_log_prob_ = {}
        
        for idx, c in enumerate(self.classes_):
            mask = (y == c)
            Xc = X[mask]
            nc = len(Xc)
            
            # Continuous MLE parameters: mu and var (ddof=0 for MLE 1/n)
            self.mu_[c] = Xc[NUM].mean().values
            raw_var = Xc[NUM].var(ddof=0).values
            self.var_[c] = np.maximum(raw_var, self.floor)
            
            # Categorical Laplace smoothed parameters
            for f in CAT:
                K_vals = self.category_sets[f]
                K_count = len(K_vals)
                # Smoothed denominator: nc + alpha * |K|
                denom = nc + self.alpha * K_count
                
                probs = {}
                for v in K_vals:
                    cnt = np.sum(Xc[f] == v)
                    probs[v] = np.log((cnt + self.alpha) / denom)
                self.cat_log_probs_[(c, f)] = probs
                
                # Unseen category log-probability: count = 0 -> alpha / denom
                self.cat_unseen_log_prob_[(c, f)] = np.log(self.alpha / denom)
                
        return self

    def _joint_log_likelihood(self, X):
        out = np.zeros((len(X), len(self.classes_)))
        for i, c in enumerate(self.classes_):
            # Prior + Gaussian log-likelihood
            var_c = self.var_[c]
            mu_c = self.mu_[c]
            x_num = X[NUM].values
            
            gauss_ll = -0.5 * np.log(2 * np.pi * var_c) - ((x_num - mu_c) ** 2) / (2 * var_c)
            ll = self.log_prior_[i] + np.sum(gauss_ll, axis=1)
            
            # Add categorical log-likelihoods
            for f in CAT:
                col_vals = X[f].values
                f_map = self.cat_log_probs_[(c, f)]
                unseen_lp = self.cat_unseen_log_prob_[(c, f)]
                cat_ll = np.array([f_map.get(v, unseen_lp) for v in col_vals])
                ll = ll + cat_ll
                
            out[:, i] = ll
        return out

    def predict_proba(self, X):
        log_ll = self._joint_log_likelihood(X)
        # Log-sum-exp trick for numerical stability
        max_log = np.max(log_ll, axis=1, keepdims=True)
        exp_ll = np.exp(log_ll - max_log)
        proba = exp_ll / np.sum(exp_ll, axis=1, keepdims=True)
        return proba

    def predict(self, X, threshold=0.5):
        proba = self.predict_proba(X)
        return (proba[:, 1] >= threshold).astype(int)

def fitpred(name, Xtr, ytr, Xte):
    if name == 'Mixed NB':
        clf = MixedNB().fit(Xtr, ytr)
        return clf.predict_proba(Xte)[:, 1]
    elif name.startswith('Gaussian'):
        gnb = GaussianNB().fit(Xtr[NUM], ytr)
        return gnb.predict_proba(Xte[NUM])[:, 1]
    elif name.startswith('Logistic'):
        # One-hot encode cp with all 4 levels explicitly
        Xd = pd.get_dummies(Xtr[NUM + CAT], columns=['cp'], dtype=float)
        Xe = pd.get_dummies(Xte[NUM + CAT], columns=['cp'], dtype=float)
        Xe = Xe.reindex(columns=Xd.columns, fill_value=0.0)
        lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42))
        lr.fit(Xd, ytr)
        return lr.predict_proba(Xe)[:, 1]
    elif name == 'Decision tree (fixed)':
        tree_cols = NUM + [f'cp_{v}' for v in CATEGORY_SETS['cp']] + [f'exang_{v}' for v in CATEGORY_SETS['exang']]
        Xd = pd.get_dummies(Xtr[NUM + CAT], columns=CAT, dtype=float).reindex(columns=tree_cols, fill_value=0.0)
        Xe = pd.get_dummies(Xte[NUM + CAT], columns=CAT, dtype=float).reindex(columns=tree_cols, fill_value=0.0)
        clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=42)
        clf.fit(Xd, ytr)
        return clf.predict_proba(Xe)[:, 1]
    else:
        raise ValueError(f"Unknown model {name}")

def metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_true, y_prob)
    except Exception:
        auc = 0.5
    brier = brier_score_loss(y_true, y_prob)
    return {
        'acc': float(acc),
        'prec': float(prec),
        'rec': float(rec),
        'spec': float(spec),
        'f1': float(f1),
        'auc': float(auc),
        'brier': float(brier),
        'tp': int(tp),
        'fp': int(fp),
        'fn': int(fn),
        'tn': int(tn)
    }

X = d[NUM + CAT]
y = d['C'].values
model_names = ['Mixed NB', 'Gaussian NB (numeric)', 'Logistic regression', 'Decision tree (fixed)']

R = {
    'dataset_source': 'UCI Cleveland Clinic Foundation (processed.cleveland.data)',
    'n_total': int(len(d)),
    'pos_cases': int(np.sum(y == 1)),
    'neg_cases': int(np.sum(y == 0)),
    'target_encoding': '0: <50% stenosis (no disease), 1: >=50% stenosis (disease)',
    'features': {'numeric': NUM, 'categorical': CAT}
}

# 2. Holdout evaluation (80/20 stratified, seed 42)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
R['holdout'] = {}
holdout_probs = {}

for name in model_names:
    p = fitpred(name, Xtr, ytr, Xte)
    holdout_probs[name] = p
    R['holdout'][name] = metrics(yte, p)

# Bootstrap 95% CIs on holdout
rng = np.random.default_rng(0)
R['holdout_ci'] = {}
for name in model_names:
    bs_acc = []
    bs_auc = []
    p_arr = holdout_probs[name]
    for _ in range(1000):
        idx = rng.integers(0, len(yte), len(yte))
        if len(np.unique(yte[idx])) < 2:
            continue
        m = metrics(yte[idx], p_arr[idx])
        bs_acc.append(m['acc'])
        bs_auc.append(m['auc'])
    R['holdout_ci'][name] = {
        'acc': [float(np.percentile(bs_acc, 2.5)), float(np.percentile(bs_acc, 97.5))],
        'auc': [float(np.percentile(bs_auc, 2.5)), float(np.percentile(bs_auc, 97.5))]
    }

# 3. Repeated Stratified 5-Fold Cross-Validation (10 repeats = 50 folds)
rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=1)
cv_records = {n: [] for n in model_names}
oof_probs = {n: np.zeros(len(y)) for n in model_names}
oof_counts = np.zeros(len(y))

for tr_idx, te_idx in rcv.split(X, y):
    X_train_f, y_train_f = X.iloc[tr_idx], y[tr_idx]
    X_test_f, y_test_f = X.iloc[te_idx], y[te_idx]
    
    for name in model_names:
        p_fold = fitpred(name, X_train_f, y_train_f, X_test_f)
        cv_records[name].append(metrics(y_test_f, p_fold))
        oof_probs[name][te_idx] += p_fold
        
    oof_counts[te_idx] += 1

for name in model_names:
    oof_probs[name] /= oof_counts

R['pooled_oof_auc'] = {
    name: float(roc_auc_score(y, oof_probs[name])) for name in model_names
}
R['threshold_sweep'] = {
    str(t): {
        'recall': metrics(y, oof_probs['Mixed NB'], threshold=t)['rec'],
        'specificity': metrics(y, oof_probs['Mixed NB'], threshold=t)['spec']
    }
    for t in [0.30, 0.35, 0.40, 0.50]
}

metric_keys = ['acc', 'prec', 'rec', 'spec', 'f1', 'auc', 'brier']
R['cv'] = {
    name: {
        k: [
            float(np.mean([m[k] for m in cv_records[name]])),
            float(np.std([m[k] for m in cv_records[name]]))
        ] for k in metric_keys
    } for name in model_names
}

# Paired differences on AUC across 50 folds
auc_mixed = np.array([m['auc'] for m in cv_records['Mixed NB']])
auc_lr = np.array([m['auc'] for m in cv_records['Logistic regression']])
auc_gnb = np.array([m['auc'] for m in cv_records['Gaussian NB (numeric)']])

R['auc_diff_mixed_vs_lr'] = [float(np.mean(auc_mixed - auc_lr)), float(np.std(auc_mixed - auc_lr))]
R['auc_diff_mixed_vs_gnb'] = [float(np.mean(auc_mixed - auc_gnb)), float(np.std(auc_mixed - auc_gnb))]
wilcoxon_res = stats.wilcoxon(auc_mixed, auc_lr)
R['wilcoxon_mixed_vs_lr_p'] = float(wilcoxon_res.pvalue)

# 4. Statistical diagnostics & EDA
R['classmeans'] = {
    str(c): d.groupby('C')[NUM].mean().round(2).to_dict('index')[c] for c in [0, 1]
}
R['class_std'] = {
    str(c): d.groupby('C')[NUM].std().round(2).to_dict('index')[c] for c in [0, 1]
}
R['shapiro'] = {
    f"{f}|{c}": float(stats.shapiro(d.loc[d['C'] == c, f]).pvalue) for f in NUM for c in [0, 1]
}
R['skew'] = {f: float(stats.skew(d[f])) for f in NUM}
R['cp_by_class'] = pd.crosstab(d['cp'], d['C']).to_dict()
R['exang_by_class'] = pd.crosstab(d['exang'], d['C']).to_dict()

# Within-class correlation matrices
within_class_corr = d[NUM].groupby(d['C']).apply(lambda g: g.corr())
R['within_class_corr'] = {
    str(c): d.loc[d['C'] == c, NUM].corr().round(3).to_dict() for c in [0, 1]
}
# Max off-diagonal correlation
wc_0 = d.loc[d['C'] == 0, NUM].corr().values
wc_1 = d.loc[d['C'] == 1, NUM].corr().values
mask_offdiag = ~np.eye(4, dtype=bool)
R['within_class_corr_maxabs_offdiag'] = float(max(np.abs(wc_0[mask_offdiag]).max(), np.abs(wc_1[mask_offdiag]).max()))

with open('results.json', 'w') as f:
    json.dump(R, f, indent=2)

print("Saved regenerated results.json successfully.")

# ----------------- REGENERATE ALL FIGURES -----------------
C0, C1 = '#1f77b4', '#d62728'

# Figure 1: Class-conditional fitted Gaussian densities
fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.0))
feature_labels = {
    'age': 'Age (years)',
    'trestbps': 'Resting BP (mm Hg)',
    'chol': 'Cholesterol (mg/dl)',
    'thalach': 'Max HR (bpm)'
}
for ax, f in zip(axes, NUM):
    for c, col, lbl in [(0, C0, 'No disease'), (1, C1, 'CAD present')]:
        vals = d.loc[d['C'] == c, f]
        ax.hist(vals, bins=12, density=True, alpha=0.35, color=col)
        xs = np.linspace(d[f].min() * 0.9, d[f].max() * 1.1, 200)
        ax.plot(xs, stats.norm.pdf(xs, vals.mean(), vals.std(ddof=0)), color=col, lw=1.3, label=lbl)
    ax.set_xlabel(feature_labels[f], fontsize=7)
    ax.set_yticks([])
    ax.tick_params(labelsize=6)
axes[0].legend(frameon=False, fontsize=6)
axes[0].set_ylabel('Density', fontsize=7)
plt.tight_layout()
plt.savefig('figs/f1.pdf', bbox_inches='tight')
plt.savefig('figs/f1.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 2: Class balance and categorical distributions
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.0))
axes[0].bar(['No disease', 'CAD present'], [R['neg_cases'], R['pos_cases']], color=[C0, C1], width=0.5)
axes[0].set_ylabel('Number of records', fontsize=7)
axes[0].set_title('Cohort Balance', fontsize=7.5)
axes[0].tick_params(labelsize=6)

cat_titles = {'cp': 'Chest Pain Type (1-4)', 'exang': 'Exercise Angina (0/1)'}
for ax, f in zip(axes[1:], CAT):
    ct = pd.crosstab(d[f], d['C'], normalize='columns')
    idx = np.arange(len(ct))
    ax.bar(idx - 0.2, ct[0], 0.4, color=C0, label='No disease')
    ax.bar(idx + 0.2, ct[1], 0.4, color=C1, label='CAD present')
    ax.set_xticks(idx)
    ax.set_xticklabels(ct.index, fontsize=6)
    ax.set_xlabel(cat_titles[f], fontsize=7)
    ax.set_ylabel('P(value | class)', fontsize=7)
    ax.tick_params(labelsize=6)
axes[1].legend(frameon=False, fontsize=6)
plt.tight_layout()
plt.savefig('figs/f2.pdf', bbox_inches='tight')
plt.savefig('figs/f2.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 3: Within-class correlation heatmaps
fig, axes = plt.subplots(1, 2, figsize=(5.8, 2.4), constrained_layout=True)
for ax, c in zip(axes, [0, 1]):
    cm = d.loc[d['C'] == c, NUM].corr()
    im = ax.imshow(cm, vmin=-1, vmax=1, cmap='RdBu_r')
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(NUM, rotation=45, fontsize=6.5)
    ax.set_yticklabels(NUM, fontsize=6.5)
    ax.set_title(['Class 0 (No disease)', 'Class 1 (CAD present)'][c], fontsize=7.5)
    for i in range(4):
        for j in range(4):
            val_txt = f"{cm.values[i, j]:.2f}"
            ax.text(j, i, val_txt, ha='center', va='center', fontsize=6,
                    color='white' if abs(cm.values[i, j]) > 0.55 else 'black')
cbar = fig.colorbar(im, ax=axes, shrink=0.82, pad=0.03)
cbar.set_label('Pearson r', fontsize=7)
cbar.ax.tick_params(labelsize=6)
plt.savefig('figs/f3.pdf', bbox_inches='tight')
plt.savefig('figs/f3.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 4: Pooled out-of-fold ROC and Calibration Curves
fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6))
cols = {'Mixed NB': '#d62728', 'Gaussian NB (numeric)': '#7f7f7f', 'Logistic regression': '#1f77b4', 'Decision tree (fixed)': '#2ca02c'}
for n in model_names:
    c = cols[n]
    fpr, tpr, _ = roc_curve(y, oof_probs[n])
    auc_val = R['pooled_oof_auc'][n]
    axes[0].plot(fpr, tpr, color=c, lw=1.2, label=f"{n} ({auc_val:.3f})")
    
    pt, pp = calibration_curve(y, oof_probs[n], n_bins=8, strategy='quantile')
    axes[1].plot(pp, pt, 'o-', color=c, ms=3.5, lw=1.1, label=n)

axes[0].plot([0, 1], [0, 1], 'k--', lw=0.7)
axes[0].set_xlabel('False Positive Rate', fontsize=7)
axes[0].set_ylabel('True Positive Rate', fontsize=7)
axes[0].legend(frameon=False, fontsize=6, loc='lower right')
axes[0].set_title('(a) Out-of-fold ROC Curves', fontsize=7.5)
axes[0].tick_params(labelsize=6)

axes[1].plot([0, 1], [0, 1], 'k--', lw=0.7)
axes[1].set_xlabel('Mean Predicted Probability', fontsize=7)
axes[1].set_ylabel('Fraction with CAD', fontsize=7)
axes[1].set_title('(b) Reliability Calibration Diagram', fontsize=7.5)
axes[1].legend(frameon=False, fontsize=6)
axes[1].tick_params(labelsize=6)

plt.tight_layout()
plt.savefig('figs/f4.pdf', bbox_inches='tight')
plt.savefig('figs/f4.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 5: Repeated Cross-Validation Metric Bars
fig, ax = plt.subplots(figsize=(6.4, 2.5))
w = 0.19
display_keys = ['acc', 'prec', 'rec', 'spec', 'f1', 'auc']
display_labels = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1', 'ROC-AUC']

for i, n in enumerate(model_names):
    c = cols[n]
    means = [R['cv'][n][k][0] for k in display_keys]
    stds = [R['cv'][n][k][1] for k in display_keys]
    ax.bar(np.arange(6) + (i - (len(model_names) - 1) / 2) * w, means, w, yerr=stds, color=c, label=n, capsize=1.5, error_kw={'lw': 0.6})

ax.set_xticks(range(6))
ax.set_xticklabels(display_labels, fontsize=6.5)
ax.set_ylim(0.5, 1.0)
ax.set_ylabel('Mean metric value', fontsize=7)
ax.legend(frameon=False, fontsize=5.5, ncol=2, loc='upper center')
ax.tick_params(labelsize=6)
plt.tight_layout()
plt.savefig('figs/f5.pdf', bbox_inches='tight')
plt.savefig('figs/f5.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 6: Confusion Matrices for Holdout Set
fig, axes = plt.subplots(1, 2, figsize=(4.8, 2.1))
for ax, n in zip(axes, ['Mixed NB', 'Logistic regression']):
    m = R['holdout'][n]
    # Matrix format: Actual 1 (top row: TP, FN), Actual 0 (bottom row: FP, TN)
    cmx = np.array([[m['tp'], m['fn']], [m['fp'], m['tn']]])
    im = ax.imshow(cmx, cmap='Blues')
    for i in range(2):
        for j in range(2):
            val = int(cmx[i, j])
            ax.text(j, i, str(val), ha='center', va='center', fontsize=9,
                    color='white' if val > 15 else 'black')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Pred 1', 'Pred 0'], fontsize=6.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Actual 1', 'Actual 0'], fontsize=6.5)
    ax.set_title(f"{n} (Holdout)", fontsize=7.5)
plt.tight_layout()
plt.savefig('figs/f6.pdf', bbox_inches='tight')
plt.savefig('figs/f6.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 7: Decision Threshold Sweep for Mixed NB
ths = np.linspace(0.05, 0.95, 50)
fig, ax = plt.subplots(figsize=(3.4, 2.2))
recalls = []
specificities = []
for t in ths:
    y_pred_t = (oof_probs['Mixed NB'] >= t).astype(int)
    recalls.append(recall_score(y, y_pred_t))
    tn, fp, fn, tp = confusion_matrix(y, y_pred_t, labels=[0, 1]).ravel()
    specificities.append(tn / (tn + fp))

ax.plot(ths, recalls, label='Recall (Sensitivity)', color=C1, lw=1.3)
ax.plot(ths, specificities, label='Specificity', color=C0, lw=1.3)
ax.axvline(0.5, color='black', ls=':', lw=0.8, label='Default thr (0.5)')
ax.set_xlabel('Decision Threshold', fontsize=7)
ax.set_ylabel('Metric Value', fontsize=7)
ax.set_title('Mixed NB: Operating Threshold Sweep', fontsize=7.5)
ax.legend(frameon=False, fontsize=5.5)
ax.tick_params(labelsize=6)
plt.tight_layout()
plt.savefig('figs/f7.pdf', bbox_inches='tight')
plt.savefig('figs/f7.png', bbox_inches='tight', dpi=300)
plt.close()

print("All figures successfully regenerated in 'figs/'.")
