import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('app_copy',Path('app/copy.py')); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
def test_copy_safety_and_labels():
    text=' '.join(v for v in vars(mod).values() if isinstance(v,str)).lower()
    assert 'no symptoms' not in text and 'you have' not in text
    assert 'Asymptomatic' in mod.CP_LABELS[4]
