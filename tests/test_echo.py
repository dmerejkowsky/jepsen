from jepsen_katas.echo import EchoNode, EchoOk
from jepsen_katas.node import OutMessage, parse_message
from dataclasses import asdict


def test_parse_echo() -> None:
    json_message = {
        "src": "c1",
        "dest": "n1",
        "body": {
            "type": "echo",
            "msg_id": 1,
            "echo": "Please echo 45",
        },
    }
    message = parse_message(json_message)
    node = EchoNode()
    echo = node.parse_echo(message.body)
    assert echo.echo == "Please echo 45"


def test_serialize_echo_ok() -> None:
    echo_ok = EchoOk("yolo")
    message = OutMessage("n1", "c1", 3, 2, "echo_ok", echo_ok)
    as_dict = {
        "src": message.src,
        "dest": message.dest,
        "body": {
            "msg_id": message.msg_id,
            "in_reply_to": message.in_reply_to,
            "type": message.type,
            **asdict(message.body),
        },
    }
    assert as_dict == {
        "src": "n1",
        "dest": "c1",
        "body": {
            "type": "echo_ok",
            "msg_id": 3,
            "in_reply_to": 2,
            "echo": "yolo",
        },
    }


def test_reply_to_echo() -> None:
    json_message = {
        "dest": "n1",
        "src": "c1",
        "body": {
            "type": "echo",
            "msg_id": 1,
            "echo": "hello, there",
        },
    }
    message = parse_message(json_message)

    node = EchoNode()
    node.on_message(message)
