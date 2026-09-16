# conftest.py — bootstrap sys.path so tests can import qa_poc.* and trusted.*
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)  # qualification-admission-local-poc-v0.1/
if PKG not in sys.path:
    sys.path.insert(0, PKG)
