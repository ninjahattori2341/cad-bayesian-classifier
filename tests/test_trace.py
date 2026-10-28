import json
import sys

sys.path.insert(0,'app')
from nb_model import MixedNaiveBayes
from paths import DATA_CSV
from trace_core import build_trace, sklearn_posterior


def test_trace_is_serialisable(frame):
    model=MixedNaiveBayes().fit(frame); values=frame.iloc[0].drop('target').to_dict(); trace=build_trace(model,values,DATA_CSV)
    json.dumps(trace); assert abs(trace['log_sum_exp']['posterior']-model.predict_one(values).probability)<1e-12; assert abs(sklearn_posterior(DATA_CSV,values)-trace['log_sum_exp']['posterior'])<1e-9
