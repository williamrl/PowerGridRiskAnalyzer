from src.graph import Graph


def load_example_graph():
    g = Graph()
    # slightly larger toy graph
    g.add_edge("A", "B", 4.0, eid="e1")
    g.add_edge("B", "C", 7.0, eid="e2")
    g.add_edge("C", "D", 2.0, eid="e3")
    g.add_edge("D", "E", 5.0, eid="e4")
    g.add_edge("E", "A", 6.0, eid="e5")
    g.add_edge("B", "D", 3.0, eid="e6")
    return g


GENERATORS = ["A", "E"]
