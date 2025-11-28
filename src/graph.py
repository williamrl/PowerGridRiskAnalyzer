"""
Enhanced graph module for Power Grid Failure Risk Analyzer (Hurricanes).

Features added:
- `Edge` dataclass with `strength`, optional `capacity` and `reinforce_cost`.
- Kruskal-based reinforcement plan using `reinforce_cost`.
- Greedy prioritization for selecting top-K edges to reinforce under a wind scenario.
- Helpers for connected components and blackout zone detection (relative to generators).
- Simulation harness to run a wind event with optional reinforcements.

This file contains a compact, testable implementation intended as a foundation.
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Optional, Tuple, Dict


@dataclass
class Edge:
    id: str
    u: str
    v: str
    strength: float
    capacity: Optional[float] = None
    reinforce_cost: Optional[float] = None

    def effective_reinforce_cost(self) -> float:
        # If explicit cost not provided, derive a simple inverse-of-strength cost.
        if self.reinforce_cost is not None:
            return float(self.reinforce_cost)
        # Avoid division by zero; stronger edges cost less to 'reinforce' in this heuristic.
        return 1.0 / (self.strength + 1e-6)


class UnionFind:
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, x: str) -> str:
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, x: str, y: str) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank.get(rx, 0) < self.rank.get(ry, 0):
            self.parent[rx] = ry
        else:
            self.parent[ry] = rx
            if self.rank.get(rx, 0) == self.rank.get(ry, 0):
                self.rank[rx] = self.rank.get(rx, 0) + 1
        return True


class Graph:
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[Edge] = []

    def add_node(self, node: str):
        self.nodes.add(node)

    def add_edge(self, u: str, v: str, strength: float, *, capacity: Optional[float] = None,
                 reinforce_cost: Optional[float] = None, eid: Optional[str] = None):
        """Add an undirected edge.

        `strength`: higher means stronger (less likely to fail under wind).
        `reinforce_cost`: optional explicit cost to reinforce this edge.
        """
        self.add_node(u)
        self.add_node(v)
        if eid is None:
            eid = f"{u}-{v}-{len(self.edges)}"
        self.edges.append(Edge(id=eid, u=u, v=v, strength=float(strength), capacity=capacity,
                               reinforce_cost=reinforce_cost))

    def kruskal_reinforcement_plan(self) -> List[Edge]:
        """Return a minimal-cost set of edges (MST) based on `effective_reinforce_cost`.

        This treats the `effective_reinforce_cost` as the weight for Kruskal.
        """
        sorted_edges = sorted(self.edges, key=lambda e: e.effective_reinforce_cost())
        uf = UnionFind()
        for n in self.nodes:
            uf.parent[n] = n
            uf.rank[n] = 0
        mst: List[Edge] = []
        for e in sorted_edges:
            if uf.union(e.u, e.v):
                mst.append(e)
            if len(mst) == len(self.nodes) - 1:
                break
        return mst

    def _adj_from_edges(self, edges: List[Edge]):
        adj = defaultdict(list)
        for e in edges:
            adj[e.u].append(e.v)
            adj[e.v].append(e.u)
        return adj

    def connected_components(self, edges_subset: Optional[List[Edge]] = None) -> List[Set[str]]:
        """Return connected components considering only `edges_subset` (or all edges).
        """
        edges = edges_subset if edges_subset is not None else self.edges
        adj = self._adj_from_edges(edges)
        visited: Set[str] = set()
        comps: List[Set[str]] = []
        for n in self.nodes:
            if n in visited:
                continue
            stack = [n]
            comp: Set[str] = set()
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                comp.add(cur)
                for nei in adj.get(cur, []):
                    if nei not in visited:
                        stack.append(nei)
            comps.append(comp)
        return comps

    def simulate_wind_failures(self, wind_speed: float, edges: Optional[List[Edge]] = None) -> Tuple[List[Edge], List[Edge]]:
        """Simulate failures: edges with `strength` < `wind_speed` fail.
        Returns (surviving_edges, failed_edges).
        """
        use_edges = edges if edges is not None else self.edges
        surviving: List[Edge] = []
        failed: List[Edge] = []
        for e in use_edges:
            if e.strength < wind_speed:
                failed.append(e)
            else:
                surviving.append(e)
        return surviving, failed

    def blackout_zones(self, generators: Set[str], edges_subset: Optional[List[Edge]] = None) -> List[Set[str]]:
        """Return components that do NOT contain any generator (i.e., blackout zones).

        `generators` should be a set of node IDs representing power sources.
        """
        comps = self.connected_components(edges_subset)
        blackout = [c for c in comps if c.isdisjoint(generators)]
        return blackout

    def simulate_with_reinforcements(self, wind_speed: float, reinforced_edge_ids: Optional[Set[str]] = None) -> Dict:
        """Run a wind simulation where edges in `reinforced_edge_ids` are treated as reinforced.

        Reinforced edges are simulated with very high strength (so they survive the wind).
        Returns a dictionary with surviving, failed, components and blackout zones (no generators by default).
        """
        reinforced_edge_ids = reinforced_edge_ids or set()
        # Create a simulated list of edges where reinforced edges get a large strength.
        sim_edges: List[Edge] = []
        for e in self.edges:
            if e.id in reinforced_edge_ids:
                sim_edges.append(Edge(id=e.id, u=e.u, v=e.v, strength=max(e.strength, wind_speed + 1.0),
                                      capacity=e.capacity, reinforce_cost=e.reinforce_cost))
            else:
                sim_edges.append(e)

        surviving, failed = self.simulate_wind_failures(wind_speed, sim_edges)
        comps = self.connected_components(surviving)
        result = {
            "surviving": surviving,
            "failed": failed,
            "components": comps,
        }
        return result

    def greedy_select_top_k_reinforcements(self, wind_speed: float, k: int) -> List[str]:
        """Greedy selection of up to `k` edges to reinforce under `wind_speed`.

        Scoring heuristic: benefit = reduction in number of failed edges if this edge alone were reinforced.
        Score = benefit / cost. We pick top-k by this score (without recomputing interactions).
        This is a simple baseline; later improvements can evaluate combined effects.
        """
        baseline_surviving, baseline_failed = self.simulate_wind_failures(wind_speed)
        baseline_failed_count = len(baseline_failed)
        candidates: List[Tuple[float, str]] = []  # (score, edge_id)
        for e in self.edges:
            if e.strength >= wind_speed:
                # already survives, no need to reinforce
                continue
            # simulate reinforcing this edge only
            sim_edges = []
            for ee in self.edges:
                if ee.id == e.id:
                    sim_edges.append(Edge(id=ee.id, u=ee.u, v=ee.v, strength=max(ee.strength, wind_speed + 1.0),
                                          capacity=ee.capacity, reinforce_cost=ee.reinforce_cost))
                else:
                    sim_edges.append(ee)
            _, failed_after = self.simulate_wind_failures(wind_speed, sim_edges)
            benefit = baseline_failed_count - len(failed_after)
            cost = e.effective_reinforce_cost()
            score = (benefit / cost) if cost > 0 else float('inf')
            candidates.append((score, e.id))
        # pick top-k by score
        candidates.sort(key=lambda x: x[0], reverse=True)
        selected = [eid for _, eid in candidates[:k]]
        return selected


if __name__ == "__main__":
    # Tiny demonstration with a toy graph and reinforcement selection
    g = Graph()
    g.add_edge("A", "B", 5.0)
    g.add_edge("B", "C", 8.0)
    g.add_edge("C", "D", 3.0)
    g.add_edge("A", "D", 10.0)
    g.add_edge("B", "D", 6.0)

    print("Nodes:", sorted(g.nodes))
    print("Edges:")
    for e in g.edges:
        print(f"  {e.id}: {e.u}-{e.v} strength={e.strength} cost={e.effective_reinforce_cost():.4f}")

    print("\nKruskal reinforcement plan (MST by cost):")
    mst = g.kruskal_reinforcement_plan()
    for e in mst:
        print(f"  {e.id}: {e.u}-{e.v} cost={e.effective_reinforce_cost():.4f}")

    wind = 7.0
    print(f"\nSimulating wind speed = {wind} (edges with strength < wind fail):")
    surv, failed = g.simulate_wind_failures(wind)
    print("Failed edges:", [f.id for f in failed])
    print("Surviving edges:", [s.id for s in surv])

    print("\nGreedy choose top-1 reinforcement under this wind:")
    sel = g.greedy_select_top_k_reinforcements(wind, 1)
    print(sel)

    res = g.simulate_with_reinforcements(wind, set(sel))
    print("After reinforcement, failed:", [f.id for f in res['failed']])
