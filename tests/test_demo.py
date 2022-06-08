from fastapi.testclient import TestClient

from oxeo.api.app import app

client = TestClient(app)


def test_demo():
    assert True
