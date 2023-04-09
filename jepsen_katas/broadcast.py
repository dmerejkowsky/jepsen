from collections import defaultdict
from dataclasses import dataclass

from jepsen_katas.node import Node, Sender, log
from typing import Any


@dataclass
class Broadcast:
    message: int


@dataclass
class BroadcastOk:
    pass


@dataclass
class Read:
    pass


@dataclass
class ReadOk:
    messages: list[int]


@dataclass
class Topology:
    topology: dict[str, list[str]]


@dataclass
class TopologyOk:
    pass


class BroadcastNode(Node):
    def __init__(self, sender: Sender | None = None) -> None:
        super().__init__(sender)
        self.neighbors: list[str] = []
        self.messages: set[int] = set()
        self.sent: dict[str, set[int]] = defaultdict(set)

    def parse_broadcast(self, body: dict[str, Any]) -> Broadcast:
        return Broadcast(body["message"])

    def parse_broadcast_ok(self, body: dict[str, Any]) -> BroadcastOk:
        return BroadcastOk()

    def parse_read(self, body: dict[str, Any]) -> Read:
        return Read()

    def parse_topology(self, body: dict[str, Any]) -> Topology:
        return Topology(body["topology"])

    def handle_broadcast(self, src: str, message_id: int, broadcast: Broadcast) -> None:
        self.messages.add(broadcast.message)
        for neighbor in self.neighbors:
            already_sent = self.sent.get(neighbor, set())
            if broadcast.message not in already_sent:
                log(self.node_id, "->", neighbor, broadcast.message)
                self.send(
                    neighbor, message_id, "broadcast", Broadcast(broadcast.message)
                )
                self.sent[neighbor].add(broadcast.message)
        self.send(src, message_id, "broadcast_ok", BroadcastOk())

    def handle_read(self, src: str, message_id: int, read: Read) -> None:
        self.send(src, message_id, "read_ok", ReadOk(sorted(self.messages)))

    def handle_topology(self, src: str, message_id: int, topology: Topology) -> None:
        self.neighbors = topology.topology.get(self.node_id, [])
        log("Neighbors for", self.node_id, self.neighbors)
        self.send(src, message_id, "topology_ok", TopologyOk())

    def handle_broadcast_ok(
        self, src: str, message_id: int, broadcast_ok: BroadcastOk
    ) -> None:
        pass


def main() -> None:
    node = BroadcastNode()
    node.run()


if __name__ == "__main__":
    main()
