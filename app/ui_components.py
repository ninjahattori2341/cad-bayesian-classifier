from html import escape


def big_number(p):
    return "<1%" if p < .01 else ">99%" if p > .99 else f"{p:.1%}"
def eyebrow(text): return f'<div class="eyebrow">{escape(text)}</div>'
def chip(text, kind="info", filled=True): return f'<span class="chip chip-{escape(kind)} {"chip-filled" if filled else ""}">{escape(text)}</span>'
def stat_tile(label,value,help=None): return f'<div class="stat-tile"><div class="muted">{escape(label)}</div><strong>{escape(value)}</strong>{f"<small>{escape(help)}</small>" if help else ""}</div>'
def prob_track(p,theta): return f'<div class="prob-track" aria-label="Probability {big_number(p)}, threshold {theta:.2f}"><span style="width:{p*100:.3f}%"></span><i style="left:{theta*100:.2f}%"></i></div><div class="track-labels"><span>0</span><span>θ {theta:.2f}</span><span>1</span></div>'
def safety_banner(compact=False): return f'<div class="safety-banner" role="note"><strong>Educational research demonstration</strong><span>{"Not a medical device or diagnostic tool." if compact else "Trained on a historical, single-site dataset. It is not a medical device or diagnostic tool."}</span></div>'
def stepper(steps): return '<nav class="stepper">'+' '.join(f'<a href="#step-{i+1}">{i+1}</a>' for i,_ in enumerate(steps))+'</nav>'
def narrate(contributions,labels):
    if not contributions: return "No feature contributions are available."
    pos=sorted(((v,k) for k,v in contributions.items() if v>0),reverse=True); neg=sorted(((abs(v),k) for k,v in contributions.items() if v<0),reverse=True)
    def names(items): return " and ".join(escape(str(labels.get(k,k))) for _,k in items[:2])
    if pos and neg: return f"{names(pos)} pushed the score toward the CAD-positive class; {names(neg)} pulled it toward control."
    if pos: return f"{names(pos)} pushed the score toward the CAD-positive class."
    return f"{names(neg)} pulled the score toward control."
