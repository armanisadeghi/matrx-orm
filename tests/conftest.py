import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "level1: no database required")
    config.addinivalue_line("markers", "level2: requires live database")
    config.addinivalue_line("markers", "schema: requires live database credentials in tests/sample_project/.env")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "/level1/" in str(item.fspath):
            item.add_marker(pytest.mark.level1)
        elif "/level2/" in str(item.fspath):
            item.add_marker(pytest.mark.level2)
        elif "/sample_project/" in str(item.fspath):
            item.add_marker(pytest.mark.schema)
