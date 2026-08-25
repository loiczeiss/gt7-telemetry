import time
from unittest.mock import MagicMock

from collector.heartbeat import HeartbeatSender
from config import HEARTBEAT_PAYLOAD, HEARTBEAT_PORT


def test_heartbeat_sends_immediately_on_start():
    mock_sock = MagicMock()
    sender = HeartbeatSender("192.168.1.10", sock=mock_sock, interval_s=10.0)
    sender.start()
    try:
        mock_sock.sendto.assert_called_with(HEARTBEAT_PAYLOAD, ("192.168.1.10", HEARTBEAT_PORT))
        assert mock_sock.sendto.call_count >= 1
    finally:
        sender.stop()


def test_heartbeat_stops_sending_after_stop():
    mock_sock = MagicMock()
    sender = HeartbeatSender("192.168.1.10", sock=mock_sock, interval_s=0.05)
    sender.start()
    sender.stop()
    mock_sock.sendto.reset_mock()
    time.sleep(0.12)
    mock_sock.sendto.assert_not_called()
