import sys

sys.path.insert(0,'app')
from ui_components import big_number, narrate, prob_track


def test_big_number_edges():
    assert [big_number(x) for x in (0,.005,.5,.995,1)]==['<1%','<1%','50.0%','>99%','>99%']
def test_track_and_narration_escape():
    assert '0.50' in prob_track(.5,.5)
    assert '<script>' not in narrate({'<x>':1},{'<x>':'<script>'})
def test_narrate_cases():
    assert 'CAD-positive' in narrate({'a':1},{'a':'age'})
    assert 'control' in narrate({'a':-1},{'a':'age'})
    assert 'pulled' in narrate({'a':1,'b':-1},{'a':'age','b':'cholesterol'})
