from typing import Any


class Node:
    def __init__(self, name: str, neighbors: list[str]) -> None:
        self.name = name
        self.neighbors = neighbors
        self.got_message = False

    def __repr__(self) -> str:
        return f"Node({self.name} " + ("[x]" if self.got_message else "[ ]") + ")"


class Network:
    def __init__(self, topology: dict[str, list[str]]) -> None:
        self.nodes: dict[str, Node] = {}
        for k, v in topology.items():
            node = Node(k, v)
            self.nodes[k] = node

    def get_node(self, name: str) -> Node:
        return self.nodes[name]

    def run(self, message: int) -> None:
        n1 = self.nodes["n1"]
        self.broadcast(n1, 42)

    def check(self) -> None:
        for node in self.nodes.values():
            assert node.got_message, f"{node.name} did not get the message"

    def broadcast(self, node: Node, message: int) -> None:
        node.got_message = True
        for name in node.neighbors:
            neighbor = self.nodes[name]
            if neighbor.got_message:
                continue
            print(node.name, "->", neighbor.name, ":", message)
            neighbor.got_message = True
            self.broadcast(neighbor, message)
