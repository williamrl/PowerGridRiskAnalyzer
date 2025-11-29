import pytest
from src.graph import Graph, Edge


def make_sample_graph():
    g = Graph()
    g.add_edge("A", "B", 5.0, eid="e1")
    g.add_edge("B", "C", 8.0, eid="e2")
    g.add_edge("C", "D", 3.0, eid="e3")
    g.add_edge("A", "D", 10.0, eid="e4")
    g.add_edge("B", "D", 6.0, eid="e5")
    return g


def test_edge_effective_cost():
    e = Edge(id="x", u="A", v="B", strength=5.0)
    # default cost = 1/strength
    assert pytest.approx(e.effective_reinforce_cost(), rel=1e-6) == 1.0 / 5.0
    e2 = Edge(id="y", u="A", v="C", strength=2.0, reinforce_cost=0.25)
    assert e2.effective_reinforce_cost() == 0.25


def test_kruskal_reinforcement_plan_has_n_minus_one_edges():
    g = make_sample_graph()
    mst = g.kruskal_reinforcement_plan()
    # MST for 4 nodes must have 3 edges
    assert len(mst) == len(g.nodes) - 1
    # edges in mst should be unique
    assert len({e.id for e in mst}) == len(mst)


def test_simulate_wind_failures_and_components():
    g = make_sample_graph()
    wind = 7.0
    surv, failed = g.simulate_wind_failures(wind)
    # e2 (8.0) and e4 (10.0) should survive; others fail
    failed_ids = {e.id for e in failed}
    assert "e3" in failed_ids
    assert "e1" in failed_ids
    # surviving edges include e2 and e4
    surv_ids = {e.id for e in surv}
    assert "e2" in surv_ids and "e4" in surv_ids
    comps = g.connected_components(surv)
    # With surviving edges A-D and B-C, the components should partition nodes
    all_nodes = set().union(*comps)
    assert all_nodes == g.nodes


def test_greedy_selection_reduces_failures():
    g = make_samplegraph()
    wind = 7.0
    # baseline failed count
    , baseline_failed = g.simulate_wind_failures(wind)
    baseline_count = len(baseline_failed)
    selected = g.greedy_select_top_k_reinforcements(wind, 1)
    assert isinstance(selected, list)
    if selected:
        res = g.simulate_with_reinforcements(wind, set(selected))
        after_failed = res["failed"]
        assert len(after_failed) <= baseline_count


def test_simulate_with_reinforcements_keeps_edge_if_reinforced():
    g = make_sample_graph()
    wind = 7.0
    # choose an edge that would fail (e3 strength 3.0)
    assert any(e.id == "e3" and e.strength < wind for e in g.edges)
    res = g.simulate_with_reinforcements(wind, {"e3"})
    failed_ids = {e.id for e in res["failed"]}
    assert "e3" not in failed_ids
