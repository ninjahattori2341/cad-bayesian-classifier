"""Single source of truth for CardioRisk visual tokens and Plotly styling."""
from pathlib import Path

import streamlit as st

LIGHT={"bg":"#f5f6f4","surface":"#ffffff","surface-2":"#eef1f0","line":"#dbe1e0","line-strong":"#b9c4c3","text":"#1c2b36","heading":"#122733","muted":"#566872","accent":"#087f73","accent-ink":"#ffffff","accent-soft":"rgba(8,127,115,.10)","case":"#087f73","control":"#4a6577","warn":"#9a6a1b","warn-bg":"#fbf3e4","warn-line":"#e6c98f","focus":"#0b5ed7"}
DARK={"bg":"#0b1118","surface":"#131d27","surface-2":"#1b2935","line":"#2c3d4a","line-strong":"#45596a","text":"#e4ebf0","heading":"#f4f7f9","muted":"#a9b9c4","accent":"#70d2c0","accent-ink":"#06211d","accent-soft":"rgba(112,210,192,.12)","case":"#70d2c0","control":"#a8bac8","warn":"#e2b66e","warn-bg":"#2a2113","warn-line":"#6b5126","focus":"#7db4ff"}
def current_theme(): return "dark" if st.session_state.get("dark_mode",False) else "light"
def tokens(theme): return dict(DARK if theme=="dark" else LIGHT)
def inject_css(theme):
    vals=tokens(theme); css=(Path(__file__).with_name("style.css")).read_text(encoding="utf-8")
    css += ":root{"+"".join(f"--{k}:{v};" for k,v in vals.items())+"}"
    css += f":root{{color-scheme:{'dark' if theme == 'dark' else 'light'};}}"
    if theme == "dark":
        css += """
        .stApp button,.stApp [role='button'],.stApp [data-baseweb] { color:var(--text)!important; }
        .stApp button svg,.stApp [role='button'] svg,.stApp [data-baseweb] svg { color:var(--text)!important; }
        .stApp button svg *, .stApp [role='button'] svg *, .stApp [data-baseweb] svg * {
          fill:var(--text)!important; stroke:var(--text)!important;
        }
        .stApp button:hover svg *, .stApp [role='button']:hover svg * {
          fill:var(--accent)!important; stroke:var(--accent)!important;
        }
        .stApp [data-testid='stWidgetLabel'] *, .stApp [data-testid='stCaptionContainer'] * {
          color:var(--text)!important;
        }
        .stApp [data-testid='stExpander'] summary svg *, .stApp [data-testid='stTooltipIcon'] svg * {
          fill:var(--muted)!important; stroke:var(--muted)!important;
        }
        """
    st.markdown(f"<style>{css}</style>",unsafe_allow_html=True)
