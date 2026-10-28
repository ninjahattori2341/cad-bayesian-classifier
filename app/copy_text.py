"""Import-safe alias for the app copy module (stdlib also has a module named copy)."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_spec=spec_from_file_location('cardiorisk_copy',Path(__file__).with_name('copy.py'))
_mod=module_from_spec(_spec); _spec.loader.exec_module(_mod)
APP_NAME=_mod.APP_NAME; SAFETY_SHORT=_mod.SAFETY_SHORT; APP_TAGLINE=_mod.APP_TAGLINE; LIMITATIONS=_mod.LIMITATIONS; DISCLOSURE=_mod.DISCLOSURE
CP_LABELS=_mod.CP_LABELS; EXANG_LABELS=_mod.EXANG_LABELS; RESULT_LABEL=_mod.RESULT_LABEL; RESULT_CAPTION=_mod.RESULT_CAPTION; PAGE_TITLE_PREDICT=_mod.PAGE_TITLE_PREDICT; PAGE_INTRO_PREDICT=_mod.PAGE_INTRO_PREDICT; CLASS_POSITIVE=_mod.CLASS_POSITIVE; CLASS_CONTROL=_mod.CLASS_CONTROL
