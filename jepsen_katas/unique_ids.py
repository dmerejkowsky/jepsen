from dataclasses import dataclass
from typing import Any

from jepsen_katas.node import Node


@dataclass
class Generate:
    pass


@dataclass
class GenerateOk:
    id: str


class UniqueIdsNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self._counter = 0

    def parse_generate(self, body: dict[str, Any]) -> Generate:
        return Generate()

    def handle_generate(self, generate: Generate) -> tuple[str, GenerateOk]:
        self._counter += 1
        id = f"{self.node_id}_{self._counter}"
        return "generate_ok", GenerateOk(id)


def main() -> None:
    node = UniqueIdsNode()
    node.run()


if __name__ == "__main__":
    main()
