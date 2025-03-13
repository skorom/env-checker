import os
import unittest
from unittest.mock import ANY, patch

from main import check_port, main, uvicorn_shutdown

TEST_EXPOSE_SEC = 10
TEST_PORT = 8080
TEST_YAML_PATH = "./test/something.yaml"


class MainTest(unittest.TestCase):
    """A unit test for the `main` function in the `main.py`, which is the entrypoint of the application."""

    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_threading = patch("main.threading").start()
        self.mock_logging = patch("main.logging").start()
        self.mock_time = patch("main.time").start()
        self.mock_os = patch("main.os").start()
        self.mock_socket = patch("main.socket.socket").start()
        self.mock_uvicorn = patch("main.uvicorn").start()
        self.mock_yaml_path = patch(
            "main.HOSTS_CHECK_YAML_PATH",
            os.path.join(os.path.dirname(__file__), "test_host_ports.yaml"),
        ).start()

    def test_uvicorn_shut_down_kills_the_process(self):
        """Shut down the application with SIGINT"""
        uvicorn_shutdown()
        self.mock_time.sleep.assert_called()
        # 9 because: 150,75,38,19,10,5,3,2,1
        self.assertEqual(9, self.mock_time.sleep.call_count)

    def test_uvicorn_shut_down_logs_every_half(self):
        """Log a message in every half before shut down called"""
        uvicorn_shutdown()
        self.mock_logging.info.assert_called()
        self.assertEqual(10, self.mock_logging.info.call_count)
        self.mock_logging.info.assert_any_call(ANY, 300)

    def test_check_port_using_socket(self):
        """Using socket to check port open"""
        test_host = "test_host"
        test_port = 1000
        mock_sock = self.mock_socket.return_value.__enter__.return_value
        self.assertEqual(0, check_port(test_host, test_port))
        mock_sock.settimeout.assert_called_with(1)
        self.assertEqual(test_host, mock_sock.connect_ex.call_args[0][0][0])
        self.assertEqual(test_port, mock_sock.connect_ex.call_args[0][0][1])

    def test_port_checking_called_for_all_host_and_ports(self):
        """Check all given hosts and ports"""
        mock_sock = self.mock_socket.return_value.__enter__.return_value
        main()
        self.assertEqual(8, mock_sock.connect_ex.call_count)
        mock_sock.connect_ex.assert_any_call(
            ("kafka-node-1", 9092)
        )
        mock_sock.connect_ex.assert_any_call(("oracle-db-domain", 6200))

    def test_log_error_when_not_enough_amount_succeed(self):
        """Minimum succeed matters"""
        mock_sock = self.mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 0
        main()
        self.assertEqual(1, self.mock_logging.error.call_count)
        self.mock_logging.error.assert_called_with(ANY, 4, 6, "kafka")

    def test_log_info_when_enough_amount_succeed(self):
        """Minimum succeed logged"""
        mock_sock = self.mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 0
        main()
        self.assertEqual(10, self.mock_logging.info.call_count)
        self.mock_logging.info.assert_any_call(ANY, "oracle-db")

    def test_log_warn_when_port_check_failed(self):
        """Port check failure is not critical (maybe others are open in the group)"""
        mock_sock = self.mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 1
        main()
        self.assertEqual(8, self.mock_logging.warning.call_count)
        self.mock_logging.warning.assert_any_call(ANY, "oracle-db-domain", 1521)

    def test_webservice_not_started_when_not_required(self):
        """Webservice not necessarily started"""
        patch(
            "main.EXPOSE_METRICS_FOR_SECONDS",
            "-",
        ).start()
        main()
        self.mock_uvicorn.run.assert_not_called()

    def test_shutdown_not_started_when_not_required(self):
        """Shut down thread not started when not required"""
        patch(
            "main.EXPOSE_METRICS_FOR_SECONDS",
            "-",
        ).start()
        main()
        self.mock_threading.Thread.assert_not_called()

    def test_webservice_started_when_required(self):
        """Webservice started when required"""
        main()
        self.mock_uvicorn.run.assert_called_with(
            "controller.prometheus_controller:app",
            host="0.0.0.0",
            port=TEST_PORT,
        )

    def test_shutdown_thread_started_with_webservice(self):
        """Shut down thread started when webservice started"""
        main()
        self.mock_threading.Thread.assert_called()
