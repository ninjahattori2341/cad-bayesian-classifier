import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'app'))
from paths import DATA_CSV


@pytest.fixture(scope='session')
def frame(): return pd.read_csv(DATA_CSV)
