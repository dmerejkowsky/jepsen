from dataclasses import asdict

from jepsen_katas.node import Init, InitOk, InMessage, Node, OutMessage, parse_message


def test_parse_init() -> None:
    json_message = {
        "dest": "n1",
        "src": "c1",
        "body": {
            "type": "init",
            "msg_id": 1,
            "node_id": "n1",
            "node_ids": ["n1"],
        },
    }
    message = parse_message(json_message)

    assert message
    assert message.msg_id == 1
    assert message.dest == "n1"
    assert message.src == "c1"
    assert message.type == "init"

    node = Node()
    init = node.parse_init(message.body)

    assert init.node_id == "n1"
    assert init.node_ids == ["n1"]


def test_serialize_init_ok() -> None:
    init_ok = InitOk()
    message = OutMessage("n1", "c1", 3, 2, "init_ok", init_ok)
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
            "type": "init_ok",
            "msg_id": 3,
            "in_reply_to": 2,
        },
    }


def test_reply_to_init() -> None:
    node = Node()
    node.message_id = 12
    init = Init("n1", ["n1"])
    message = InMessage("c1", "n1", 1, "init", asdict(init))
    node.on_message(message)

    assert node.node_id == "n1"
