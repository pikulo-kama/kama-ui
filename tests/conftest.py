import pytest
from kutil.pytest_plugin import get_module_patch


@pytest.fixture
def module_patch(get_module_patch):
    return get_module_patch("kui")
