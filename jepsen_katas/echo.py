#!/bin/python
import json
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class Echo:
    echo: str


@dataclass
class Init:
    node_id: str
    node_ids: list[str]


@dataclass
class InMessage:
    src: str
    dest: str
    msg_id: int
    body: Echo | Init


@dataclass
class EchoOk:
    echo: str


@dataclass
class InitOk:
    pass


@dataclass
class OutMessage:
    src: str
    dest: str
    msg_id: int
    in_reply_to: int
    body: EchoOk | InitOk


def read_line() -> Any:
    try:
        return input()
    except (KeyboardInterrupt, EOFError):
        return None


def log(*args: Any) -> None:
    print(*args, file=sys.stderr)


class EchoServer:
    def __init__(self) -> None:
        self.node_id: str | None = None
        self.next_message_id = 0

    def on_message(self, message: InMessage) -> OutMessage | None:
        self.next_message_id += 1
        request = message.body
        src = message.src
        body: None | EchoOk | InitOk = None
        if isinstance(request, Init):
            body = self.on_init(request)
        elif isinstance(request, Echo):
            body = self.on_echo(request)
        else:
            log("Unknow message", message)
            return None

        assert self.node_id, "should have got an 'init' message"
        return OutMessage(self.node_id, src, self.next_message_id, message.msg_id, body)

    def on_init(self, init: Init) -> InitOk:
        self.node_id = init.node_id
        log("Node id is", self.node_id)
        return InitOk()

    def on_echo(self, echo: Echo) -> EchoOk:
        return EchoOk(echo.echo)

    def run(self) -> None:
        while True:
            line = read_line()
            if line is None:
                break
            json_message = json.loads(line)
            message = parse_message(json_message)
            if not message:
                continue
            new_message = self.on_message(message)
            if not new_message:
                continue
            json_message = message_to_dict(new_message)
            print(json.dumps(json_message), flush=True)


def parse_message(json_message: dict[str, Any]) -> InMessage | None:
    json_body = json_message["body"]
    message_type = json_body["type"]
    body: None | Echo | Init = None
    if message_type == "init":
        body = Init(json_body["node_id"], json_body["node_ids"])
    elif message_type == "echo":
        body = Echo(json_body["echo"])

    if not body:
        log("Unknown message type", message_type)
        return None

    message = InMessage(
        json_message["src"], json_message["dest"], json_body["msg_id"], body
    )
    return message


def message_to_dict(message: OutMessage) -> dict[str, Any]:
    body = message.body
    json_body: dict[str, Any] = {
        "msg_id": message.msg_id,
        "in_reply_to": message.in_reply_to,
    }

    if isinstance(body, InitOk):
        json_body["type"] = "init_ok"
    elif isinstance(body, EchoOk):
        json_body["type"] = "echo_ok"
        json_body["echo"] = body.echo
    else:
        raise ValueError(f"Invalid body: {body}")

    return {
        "src": message.src,
        "dest": message.dest,
        "body": json_body,
    }


def main() -> None:
    echo_server = EchoServer()
    echo_server.run()


if __name__ == "__main__":
    main()
