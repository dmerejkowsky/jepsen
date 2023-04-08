from dataclasses import dataclass
from typing import Any

from jepsen_katas.node import Node


@dataclass
class Echo:
    echo: str


@dataclass
class EchoOk:
    echo: str


class EchoNode(Node):
    def __init__(self) -> None:
        super().__init__()

    def parse_echo(self, body: dict[str, Any]) -> Echo:
        return Echo(body["echo"])

    def handle_echo(self, echo: Echo) -> tuple[str, EchoOk]:
        return "echo_ok", EchoOk(echo.echo)


def main() -> None:
    node = EchoNode()
    node.run()


if __name__ == "__main__":
    main()
