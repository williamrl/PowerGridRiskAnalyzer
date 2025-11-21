"""
Simple graph module for Power Grid Failure Risk Analyzer (Hurricanes).
Contains:
- UnionFind: helper for Kruskal
- Graph: nodes and edges, Kruskal MST, DFS components
- simulate_wind_failures: removes weakest edges based on wind speed

This is a lightweight starting point and is intentionally minimal.
"""
from collections import defaultdict
from typing import List, Tuple, Set

Edge = Tuple[str, str, float]  # (u, v, strength)

class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, x, y):
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

    def add_edge(self, u: str, v: str, strength: float):
        """Add an undirected edge with a numeric `strength`.
        Higher `strength` means the line is stronger (harder to fail).
        """
        self.add_node(u)
        self.add_node(v)
        self.edges.append((u, v, float(strength)))

    def kruskal_mst(self) -> List[Edge]:
        """Return edges in a Minimum Spanning Tree computed by Kruskal.
        Here we treat lower 'strength' as lower cost (i.e., weak edges are cheaper to 'reinforce').
        This is a starting interpretation; adjust weight semantics as needed.
        """
        # Sort edges by strength ascending (weak first)
        sorted_edges = sorted(self.edges, key=lambda e: e[2])
        uf = UnionFind()
        for n in self.nodes:
            uf.parent[n] = n
            uf.rank[n] = 0
        mst = []
        for u, v, s in sorted_edges:
            if uf.union(u, v):
                mst.append((u, v, s))
            if len(mst) == len(self.nodes) - 1:
                break
        return mst

    def _adj_from_edges(self, edges: List[Edge]):
        adj = defaultdict(list)
        for u, v, _ in edges:
            adj[u].append(v)
            adj[v].append(u)
        return adj

    def connected_components(self, edges_subset: List[Edge] = None) -> List[Set[str]]:
        """Return list of connected components considering only `edges_subset`.
        If `edges_subset` is None, use all edges.
        """
        edges = edges_subset if edges_subset is not None else self.edges
        adj = self._adj_from_edges(edges)
        visited = set()
        comps = []
        for n in self.nodes:
            if n in visited:
                continue
            stack = [n]
            comp = set()
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

    def simulate_wind_failures(self, wind_speed: float) -> Tuple[List[Edge], List[Edge]]:
        """Simulate failures: edges with `strength` < `wind_speed` fail first (we remove them).
        Returns a tuple (surviving_edges, failed_edges).
        """
        surviving = []
        failed = []
        for e in self.edges:
            if e[2] < wind_speed:
                failed.append(e)
            else:
                surviving.append(e)
        return surviving, failed

if __name__ == "__main__":
    # Tiny demonstration with a toy graph
    g = Graph()
    g.add_edge("A", "B", 5.0)
    g.add_edge("B", "C", 8.0)
    g.add_edge("C", "D", 3.0)
    g.add_edge("A", "D", 10.0)
    g.add_edge("B", "D", 6.0)

    print("Nodes:", sorted(g.nodes))
    print("Edges:", g.edges)

    print("\nKruskal MST (edges listed as (u,v,strength)):")
    mst = g.kruskal_mst()
    print(mst)

    wind = 7.0
    print(f"\nSimulating wind speed = {wind} (edges with strength < wind fail):")
    surv, failed = g.simulate_wind_failures(wind)
    print("Failed edges:", failed)
    print("Surviving edges:", surv)

    comps = g.connected_components(surv)
    print("\nConnected components after failures:")
    for c in comps:
        print(c)
