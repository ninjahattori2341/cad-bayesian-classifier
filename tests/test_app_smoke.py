from pathlib import Path

from streamlit.testing.v1 import AppTest

APP=str(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py')
def test_app_renders_without_exception():
    at=AppTest.from_file(APP,default_timeout=60).run(); assert not at.exception
