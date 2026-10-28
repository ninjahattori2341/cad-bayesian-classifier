"""Inline SVG evidence strips for numeric model inputs."""
import math
from html import escape

W, H, PAD = 320, 56, 6
def _pdf(x, mean, var): return math.exp(-((x-mean)**2)/(2*var))/math.sqrt(2*math.pi*var)
def evidence_strip(feature, value, lo, hi, model, n=80):
    xs=[lo+(hi-lo)*i/(n-1) for i in range(n)]
    curves={c:[_pdf(x,model.means[c][feature],model.variances[c][feature]) for x in xs] for c in (0,1)}
    top=max(max(v) for v in curves.values()) or 1.0
    px=lambda x: PAD+(x-lo)/(hi-lo)*(W-2*PAD)
    def path(c): return "M"+" L".join(f"{px(x):.1f},{H-8-(y/top)*(H-18):.1f}" for x,y in zip(xs,curves[c]))
    vx=px(min(max(value,lo),hi)); ratio=math.log(max(_pdf(value,model.means[1][feature],model.variances[1][feature]),1e-300)/max(_pdf(value,model.means[0][feature],model.variances[0][feature]),1e-300))
    lean="toward CAD-positive" if ratio > 0 else "toward control"
    label=escape(f"{feature}: value {value:g} leans {lean} (log-likelihood ratio {ratio:+.2f})")
    return f'<svg class="evidence" viewBox="0 0 {W} {H}" role="img" aria-label="{label}"><path d="{path(0)}" class="ev-control" fill="none" stroke-width="2"/><path d="{path(1)}" class="ev-case" fill="none" stroke-width="2" stroke-dasharray="5 3"/><line x1="{vx:.1f}" x2="{vx:.1f}" y1="2" y2="{H-6}" class="ev-marker" stroke-width="2"/><circle cx="{vx:.1f}" cy="{H-8}" r="3.5" class="ev-marker-dot"/></svg>'
