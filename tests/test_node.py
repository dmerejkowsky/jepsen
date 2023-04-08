from dataclasses import asdict

from jepsen_katas.node import (
    Init,
    InitOk,
    InMessage,
    Node,
    OutMessage,
    message_to_dict,
    parse_message,
)


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
    as_dict = message_to_dict(message)
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
    node.next_message_id = 12
    init = Init("n1", ["n1"])
    message = InMessage("c1", "n1", 1, "init", asdict(init))
    print(message)
    response = node.on_message(message)

    assert response
    assert response.src == "n1"
    assert response.dest == "c1"
    assert response.msg_id == 13
    assert response.in_reply_to == 1
    assert isinstance(response.body, InitOk)
