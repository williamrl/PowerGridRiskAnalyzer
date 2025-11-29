# PowerGridRiskAnalyzer

**Setup**
- **Python:** Recommended Python 3.10+ (this project was tested with a venv using Python 3.14).
- **Create virtualenv:**

  ```powershell
  python -m venv .venv
  ```

- **Activate virtualenv (PowerShell):**

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- **Install dependencies:**

  - If you have a `requirements-dev.txt` later, use:

    ```powershell
    python -m pip install -r requirements-dev.txt
    ```

  - For the current minimal setup (tests), install `pytest` directly:

    ```powershell
    python -m pip install pytest
    ```

**Run the demo**
- A small demo runner exists in `src/graph.py`. To run the toy graph demo:

```powershell
python src\graph.py
```

This prints nodes, edges, a Kruskal-based reinforcement plan, a wind failure simulation, and a greedy reinforcement selection example.

**Run tests**
- Unit tests are under `tests/`. Run them with `pytest`:

```powershell
python -m pytest tests\test_graph.py -q
```

**Files included so far**
- `src/graph.py`: Graph model, `Edge` dataclass, Kruskal reinforcement plan, greedy reinforcement selector, simulation helpers, and a small CLI demo.
- `tests/test_graph.py`: Pytest tests covering costs, MST properties, failure simulation, greedy selection, and reinforcement behavior.

**Next steps**
- Add more unit tests (edge-cases, generator-based blackout detection, randomized stress tests).
- Add a small CLI runner `src/simulate.py` that can load JSON toy graphs and produce summarized reports.
- Scaffold a minimal web UI to visualize graphs and simulation results.

# PowerGridRiskAnalyzer