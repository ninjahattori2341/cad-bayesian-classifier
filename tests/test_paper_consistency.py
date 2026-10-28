import json

from paths import RESULTS_JSON


def test_frozen_results(frame):
    r=json.loads(RESULTS_JSON.read_text()); assert r['n_total']==len(frame); assert r['pos_cases']==139; assert r['neg_cases']==164
    assert round(r['cv']['Mixed NB']['auc'][0],3)==.831; assert round(r['cv']['Mixed NB']['brier'][0],3)==.183
