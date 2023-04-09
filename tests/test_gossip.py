from jepsen_katas.gossip import Network


def test_simple_gossip() -> None:
    topology: dict[str, list[str]] = {
        "n1": ["n2", "n3", "n4"],
        "n2": ["n3", "n4"],
        "n3": ["n1", "n2", "n6"],
        "n4": ["n5"],
        "n5": [],
        "n6": [],
    }
    network = Network(topology)
    network.run(42)
    network.check()
