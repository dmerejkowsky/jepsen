#!/bin/python
from copy import copy
import json
import sys
from dataclasses import asdict, dataclass
from typing import Any, Protocol


@dataclass
class InMessage:
    src: str
    dest: str
    msg_id: int
    type: str
    body: dict[str, Any]


@dataclass
class OutMessage:
    src: str
    dest: str
    msg_id: int
    in_reply_to: int
    type: str
    body: Any


@dataclass
class Init:
    node_id: str
    node_ids: list[str]


@dataclass
class InitOk:
    pass


def read_line() -> Any:
    try:
        return input()
    except (KeyboardInterrupt, EOFError):
        return None


def log(*args: Any) -> None:
    print(*args, file=sys.stderr)


class Sender(Protocol):
    def send(
        self,
        src: str,
        dest: str,
        message_id: int,
        in_reply_to: int,
        type: str,
        body: Any,
    ) -> None:
        pass


class JsonStdoutSender(Sender):
    def send(
        self,
        src: str,
        dest: str,
        message_id: int,
        in_reply_to: int,
        type: str,
        body: Any,
    ) -> None:
        json_message = {
            "src": src,
            "dest": dest,
            "body": {
                "msg_id": message_id,
                "in_reply_to": in_reply_to,
                "type": type,
                **asdict(body),
            },
        }
        print(json.dumps(json_message), flush=True)


class Node:
    def __init__(self, sender: Sender | None = None) -> None:
        self.node_id: str = ""
        self.message_id = 0
        if not sender:
            self._sender: Sender = JsonStdoutSender()
        else:
            self._sender = sender

    def on_message(self, message: InMessage) -> None:
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

        handle_method(message.src, message.msg_id, body)

    def send(self, dest: str, in_reply_to: int, type: str, body: Any) -> None:
        self.message_id += 1
        self._sender.send(self.node_id, dest, self.message_id, in_reply_to, type, body)

    def parse_init(self, body: dict[str, Any]) -> Init:
        return Init(body["node_id"], body["node_ids"])

    def handle_init(self, src: str, message_id: int, init: Init) -> None:
        self.node_id = init.node_id
        log("Node id is", self.node_id)
        self.send(src, message_id, "init_ok", init)

    def run(self) -> None:
        while True:
            line = read_line()
            if line is None:
                break
            json_message = json.loads(line)
            message = parse_message(json_message)
            if not message:
                continue
            self.on_message(message)


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
