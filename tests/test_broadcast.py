from jepsen_katas.broadcast import Broadcast, Topology, BroadcastNode
from jepsen_katas.node import Sender
from typing import Any


class SpySender(Sender):
    def __init__(self) -> None:
        self.sent: list[tuple[str, Any]] = []

    def send(
        self,
        src: str,
        dest: str,
        message_id: int,
        in_reply_to: int,
        type: str,
        body: Any,
    ) -> None:
        self.sent.append((dest, body))

    def get_broadcast_messages(self) -> list[tuple[str, int]]:
        return [
            (dest, b.message) for (dest, b) in self.sent if isinstance(b, Broadcast)
        ]


def test_handle_broadcast_once() -> None:
    test_sender = SpySender()
    node = BroadcastNode(test_sender)
    node.node_id = "n1"
    node.handle_topology("c1", 12, Topology({"n1": ["n2", "n3"]}))
    node.handle_broadcast("n1", 13, Broadcast(42))
    assert test_sender.get_broadcast_messages() == [("n2", 42), ("n3", 42)]


def test_skip_broadcast_if_already_sent() -> None:
    test_sender = SpySender()
    node = BroadcastNode(test_sender)
    node.node_id = "n1"
    node.handle_topology("c1", 12, Topology({"n1": ["n2", "n3"]}))
    node.handle_broadcast("n1", 13, Broadcast(42))
    node.handle_broadcast("n1", 14, Broadcast(42))
    node.handle_broadcast("n1", 15, Broadcast(43))
    assert test_sender.get_broadcast_messages() == [
        ("n2", 42),
        ("n3", 42),
        ("n2", 43),
        ("n3", 43),
    ]
