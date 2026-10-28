import sys

sys.path.insert(0,'app')
from theme import DARK, LIGHT


def lum(hex_color):
    rgb=[int(hex_color[i:i+2],16)/255 for i in (1,3,5)]
    rgb=[v/12.92 if v<=.03928 else ((v+.055)/1.055)**2.4 for v in rgb]
    return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]
def ratio(a,b):
    x,y=lum(a),lum(b); return (max(x,y)+.05)/(min(x,y)+.05)
def test_core_token_contrast():
    for t in (LIGHT,DARK):
        assert ratio(t['text'],t['bg'])>=4.5 and ratio(t['text'],t['surface'])>=4.5
        assert ratio(t['muted'],t['surface'])>=3
        assert ratio(t['accent'],t['surface'])>=3
        assert ratio(t['accent-ink'],t['accent'])>=3
