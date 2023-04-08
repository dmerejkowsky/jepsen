from jespen_katas.echo import (
    Echo,
    EchoOk,
    EchoServer,
    Init,
    InitOk,
    InMessage,
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
    assert isinstance(message.body, Init)
    init = message.body
    assert message.msg_id == 1
    assert init.node_id == "n1"
    assert init.node_ids == ["n1"]


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

    assert message
    assert isinstance(message.body, Echo)
    echo = message.body
    assert echo.echo == "Please echo 45"


def test_serialize_init_ok() -> None:
    init_ok = InitOk()
    message = OutMessage("n1", "c1", 3, 2, init_ok)
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


def test_serialize_echo_ok() -> None:
    echo_ok = EchoOk("yolo")
    message = OutMessage("n1", "c1", 3, 2, echo_ok)
    as_dict = message_to_dict(message)
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


def test_reply_to_init() -> None:
    server = EchoServer()
    server.next_message_id = 12
    init = Init("n1", ["n1"])
    message = InMessage("c1", "n1", 1, init)
    response = server.on_message(message)

    assert response
    assert response.src == "n1"
    assert response.dest == "c1"
    assert response.msg_id == 13
    assert response.in_reply_to == 1
    assert isinstance(response.body, InitOk)


def test_reply_to_echo() -> None:
    server = EchoServer()
    server.node_id = "n1"
    server.next_message_id = 12
    echo = Echo("yolo")
    message = InMessage("c1", "n1", 1, echo)
    response = server.on_message(message)

    assert response
    assert response.src == "n1"
    assert response.dest == "c1"
    assert response.msg_id == 13
    assert response.in_reply_to == 1
    body = response.body
    assert isinstance(body, EchoOk)
    assert body.echo == "yolo"
