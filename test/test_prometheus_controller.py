import unittest

from fastapi.testclient import TestClient

from app.controller.prometheus_controller import app, root

client = TestClient(app)


class TestController(unittest.IsolatedAsyncioTestCase):
    """A unit test for the `controller.py` solution.
    Note: We do not perform any REST requests.
    The tests are calling the asynchronous function directly."""

    async def test_root_controller_returns_with_json(self):
        """Request on root endpoint returns with OK"""

        response = await root()
        assert response["status"] == "up"
