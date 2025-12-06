"""CLI runner for PowerGridRiskAnalyzer toy graphs.

Usage examples:
    python -m src.simulate --file data/example_graph.py --wind 7.0 --method greedy --k 1
    python -m src.simulate --file data/example_graph.py --wind 7.0 --method mst --k 2 --out results.json

Supported methods for selecting reinforcements:
 - greedy: use `greedy_select_top_k_reinforcements`
 - mst: use Kruskal MST (take first k edges of MST)
 - none: no reinforcements

Outputs a short summary to stdout and can write a JSON results file with `--out`.
"""
import sys
from pathlib import Path

# Allow running the script directly (python src/simulate.py) by ensuring
# the project root is on sys.path so `import src.graph` works.
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
import argparse
import importlib.util
import json
import os
from typing import List, Dict, Any, Set
from src.graph import Graph


def load_graph_from_json(path: str) -> Graph:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    g = Graph()
    # edges: list of objects with u, v, strength, optional id, reinforce_cost
    for e in data.get("edges", []):
        u = e["u"]
        v = e["v"]
        strength = e.get("strength", 0.0)
        eid = e.get("id")
        rcost = e.get("reinforce_cost")
        capacity = e.get("capacity")
        g.add_edge(u, v, strength, capacity=capacity, reinforce_cost=rcost, eid=eid)
    return g


def load_graph_from_py(path: str):
    """Dynamically import a python file that provides `load_example_graph()` or `GRAPH`.

    Returns tuple (Graph, generators_list).
    """
    spec = importlib.util.spec_from_file_location("example_graph_module", path)
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError(f"Cannot load python module from {path}")
    loader.exec_module(module)
    gens = []
    if hasattr(module, "load_example_graph"):
        g = module.load_example_graph()
    elif hasattr(module, "GRAPH"):
        g = getattr(module, "GRAPH")
    else:
        raise AttributeError("Python graph module must define `load_example_graph()` or `GRAPH`")
    if hasattr(module, "GENERATORS"):
        gens = list(getattr(module, "GENERATORS"))
    return g, gens


def summarize_results(res: Dict[str, Any], generators: Set[str] = None) -> None:
    surviving = res.get("surviving", [])
    failed = res.get("failed", [])
    comps = res.get("components", [])
    print("--- Simulation Summary ---")
    print(f"Surviving edges ({len(surviving)}): {[e.id for e in surviving]}")
    print(f"Failed edges ({len(failed)}): {[e.id for e in failed]}")
    print(f"Connected components ({len(comps)}):")
    for i, c in enumerate(comps, 1):
        print(f"  C{i}: {sorted(list(c))}")
    if generators:
        # blackout zones: components disjoint from generators
        blackout = [c for c in comps if c.isdisjoint(generators)]
        print(f"Blackout zones (no generators) count: {len(blackout)}")
    print("--------------------------")

def run_simulation_to_dict(
    file: str,
    wind: float,
    method: str,
    k: int,
    generators: List[str] = None,
) -> Dict[str, Any]:
    """
    Same core logic as run_simulation, but returns a plain dict
    so the web UI can render it instead of just printing.
    """
    gens = set(generators or [])

    # Load graph either from .py module or JSON, same as run_simulation
    if file.lower().endswith(".py"):
        g, py_gens = load_graph_from_py(file)
        gens.update(py_gens)
    else:
        g = load_graph_from_json(file)

    # Choose reinforcement set
    selected: List[str] = []
    if method == "greedy":
        selected = g.greedy_select_top_k_reinforcements(wind, k)
    elif method == "mst":
        mst = g.kruskal_reinforcement_plan()
        selected = [e.id for e in mst][:k]
    elif method == "none":
        selected = []
    else:
        raise ValueError(f"unknown method: {method}")

    # Run simulation with those reinforcements
    res = g.simulate_with_reinforcements(wind, set(selected))

    # Build a serializable summary dict
    result: Dict[str, Any] = {
        "file": file,
        "wind": wind,
        "method": method,
        "k": k,
        "selected": selected,
        "surviving": [e.id for e in res.get("surviving", [])],
        "failed": [e.id for e in res.get("failed", [])],
        "components": [sorted(list(c)) for c in res.get("components", [])],
        "generators": list(gens),
        # Add graph structure for visualization
        "nodes": sorted(list(g.nodes)),
        "edges": [{"id": e.id, "u": e.u, "v": e.v, "strength": e.strength} for e in g.edges],
    }

    # blackout zones (components with no generators)
    if gens:
        blackout = [
            sorted(list(c))
            for c in g.blackout_zones(gens, res.get("surviving"))
        ]
    else:
        blackout = []

    result["blackouts"] = blackout
    return result

def run_simulation(file: str, wind: float, method: str, k: int, out: str = None, generators: List[str] = None):
    # Support python module graphs (path endswith .py) or JSON by extension
    gens = set(generators or [])
    if file.lower().endswith(".py"):
        g, py_gens = load_graph_from_py(file)
        gens.update(py_gens)
    else:
        g = load_graph_from_json(file)
    selected: List[str] = []
    if method == "greedy":
        selected = g.greedy_select_top_k_reinforcements(wind, k)
    elif method == "mst":
        mst = g.kruskal_reinforcement_plan()
        selected = [e.id for e in mst][:k]
    elif method == "none":
        selected = []
    else:
        raise ValueError(f"unknown method: {method}")

    print(f"Selected reinforcements ({len(selected)}): {selected}")
    res = g.simulate_with_reinforcements(wind, set(selected))
    # add blackout info if generators provided
    if gens:
        res["generators"] = list(gens)
        res["blackout_zones"] = [list(c) for c in g.blackout_zones(gens, res.get("surviving"))]
    summarize_results(res, gens)

    if out:
        # prepare serializable output
        out_data = {
            "selected": selected,
            "surviving": [e.id for e in res.get("surviving", [])],
            "failed": [e.id for e in res.get("failed", [])],
            "components": [list(c) for c in res.get("components", [])],
        }
        if gens:
            out_data["generators"] = list(gens)
            out_data["blackout_zones"] = [list(c) for c in g.blackout_zones(gens, res.get("surviving"))]
        with open(out, "w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=2)
        print(f"Wrote results to {out}")


def main():
    parser = argparse.ArgumentParser(description="Run a wind failure simulation on a toy graph JSON.")
    parser.add_argument("--file", "-f", required=True, help="Path to JSON graph file")
    parser.add_argument("--py", action="store_true", help="Treat `--file` as a Python module path")
    parser.add_argument("--wind", "-w", type=float, default=7.0, help="Wind speed threshold")
    parser.add_argument("--method", "-m", choices=["greedy", "mst", "none"], default="greedy",
                        help="Reinforcement selection method")
    parser.add_argument("--k", "-k", type=int, default=1, help="Number of reinforcements to select")
    parser.add_argument("--out", help="Write results to JSON file")
    parser.add_argument("--generators", "-g", nargs="*", help="List of generator node IDs (optional)")
    args = parser.parse_args()
    # if --py specified, ensure extension is .py or path is used as given
    file_path = args.file
    if args.py and not file_path.lower().endswith(".py"):
        # leave as-is; load_graph_from_py will try to import by path
        pass
    run_simulation(file_path, args.wind, args.method, args.k, out=args.out, generators=args.generators)


if __name__ == "__main__":
    main()
