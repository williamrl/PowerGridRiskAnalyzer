from src.graph import Graph


def load_example_graph() -> Graph:
    g = Graph()
    g.add_edge("A", "B", 5.0, eid="e1")
    g.add_edge("B", "C", 8.0, eid="e2")
    g.add_edge("C", "D", 3.0, eid="e3")
    g.add_edge("A", "D", 10.0, eid="e4")
    g.add_edge("B", "D", 6.0, eid="e5")
    return g


##Optional: list of generator node ids the simulator may use
GENERATORS = ["A"] 
