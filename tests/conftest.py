"""Common fixtures and configurations for this test directory."""
import os
import shutil
import sys
from pathlib import Path

# Only test support modules; runtime imports must retain qualification provenance.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest


@pytest.fixture(scope='module')
def cwd_module_dir():
    """Change current directory to this module's folder to access inputs and write outputs."""
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(cwd)


@pytest.fixture(scope='module')
def pygen_output_dir(cwd_module_dir):
    """Return an empty output directory, part of syspath to allow importing generated code."""
    path = 'output'
    shutil.rmtree(path, ignore_errors=True)
    sys.path.append(path)
    yield path
    sys.path.remove(path)
    shutil.rmtree(path, ignore_errors=False)


# Capture qualified runtime roots before tests, and reject support fixtures that
# accidentally redirect imports back into a different checkout.
def pytest_sessionstart(session):
    import pyecore, multigen, pyecoregen
    session._runtime_roots = {
        m.__name__: Path(m.__file__).resolve().parent
        for m in (pyecore, multigen, pyecoregen)
    }


def pytest_sessionfinish(session, exitstatus):
    for name, module in list(sys.modules.items()):
        root = session._runtime_roots.get(name.split('.')[0])
        if root is not None and getattr(module, '__file__', None):
            assert Path(module.__file__).resolve().is_relative_to(root), (name, module.__file__)
