from dataclasses import dataclass
from typing import Any

from jepsen_katas.node import Node, Sender


@dataclass
class Echo:
    echo: str


@dataclass
class EchoOk:
    echo: str


class EchoNode(Node):
    def __init__(self, sender: Sender | None = None) -> None:
        super().__init__(sender)

    def parse_echo(self, body: dict[str, Any]) -> Echo:
        return Echo(body["echo"])

    def handle_echo(self, dest: str, in_reply_to: int, echo: Echo) -> None:
        self.send(dest, in_reply_to, "echo_ok", EchoOk(echo.echo))


def main() -> None:
    node = EchoNode()
    node.run()


if __name__ == "__main__":
    main()
