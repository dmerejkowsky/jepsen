#!/bin/python
import json
import sys
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Init:
    node_id: str
    node_ids: list[str]


@dataclass
class InMessage:
    src: str
    dest: str
    msg_id: int
    type: str
    body: dict[str, Any]


@dataclass
class InitOk:
    type: str = "init_ok"


@dataclass
class OutMessage:
    src: str
    dest: str
    msg_id: int
    in_reply_to: int
    type: str
    body: Any


def read_line() -> Any:
    try:
        return input()
    except (KeyboardInterrupt, EOFError):
        return None


def log(*args: Any) -> None:
    print(*args, file=sys.stderr)


class Node:
    def __init__(self) -> None:
        self.node_id: str = ""
        self.next_message_id = 0

    def on_message(self, message: InMessage) -> OutMessage | None:
        message_type = message.type
        body = message.body

        method_name = "parse_" + message_type
        parse_method = getattr(self, method_name, None)
        if not parse_method:
            log("Cannot parse", message_type)
            return None

        body = parse_method(body)

        method_name = "handle_" + message_type
        handle_method = getattr(self, method_name, None)
        if not handle_method:
            log("Cannot handle", message_type)
            return None

        response_type, response = handle_method(body)

        self.next_message_id += 1
        return OutMessage(
            self.node_id,
            message.src,
            self.next_message_id,
            message.msg_id,
            response_type,
            response,
        )

    def parse_init(self, body: dict[str, Any]) -> Init:
        return Init(body["node_id"], body["node_ids"])

    def handle_init(self, init: Init) -> tuple[str, InitOk]:
        self.node_id = init.node_id
        log("Node id is", self.node_id)
        return "init_ok", InitOk()

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


def parse_message(json_message: dict[str, Any]) -> InMessage:
    json_body = json_message["body"]
    message = InMessage(
        json_message["src"],
        json_message["dest"],
        json_body["msg_id"],
        json_body["type"],
        json_body,
    )
    return message


def message_to_dict(message: OutMessage) -> dict[str, Any]:
    return {
        "src": message.src,
        "dest": message.dest,
        "body": {
            "msg_id": message.msg_id,
            "in_reply_to": message.in_reply_to,
            "type": message.type,
            **asdict(message.body),
        },
    }
