# PowerGridRiskAnalyzer

**Setup**
- **Python:** Recommended Python 3.10+
- **Create a virtual environment:**

  ```powershell
  python -m venv .venv
  ```

- **Activate the virtual environment (PowerShell):**

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- **Install dependencies:**

  ```powershell
  python -m pip install -r requirements.txt
  ```

  This installs: FastAPI, Uvicorn, Jinja2, pytest, python-multipart, and matplotlib.

**Run the Web Application**
- The main application is a FastAPI web interface. To run it:

```powershell
python -m uvicorn src.web_app:app --reload --port 8000
```

Then open your browser and navigate to `http://localhost:8000`. The web app allows you to:
- Select wind speed thresholds
- Choose reinforcement methods (greedy, MST, or none)
- Upload custom graph files or use example datasets
- Run simulations and view results

**Run the CLI Simulator**
- To run simulations from the command line using `src/simulate.py`:

```powershell
python -m src.simulate --file data/example_graph.py --wind 7.0 --method greedy --k 1
```

Supported methods: `greedy`, `mst`, `none`

Optional parameters:
- `--out <filename>`: Write results to a JSON file
- `--generators <node1,node2,...>`: Specify generator nodes for blackout analysis

**Run the Graph Demo**
- A small demo runner exists in `src/graph.py`. To run the toy graph demo:

```powershell
python src\graph.py
```

This prints nodes, edges, a Kruskal-based reinforcement plan, a wind failure simulation, and a greedy reinforcement selection example.

**Run Tests**
- Unit tests are under `tests/`. Run them with `pytest`:

```powershell
python -m pytest tests\test_graph.py -v
```

**Files included**
- `src/graph.py`: Graph model, `Edge` dataclass, Kruskal reinforcement plan, greedy reinforcement selector, simulation helpers, and a CLI demo.
- `src/simulate.py`: CLI runner for loading and simulating graphs from Python modules or JSON files.
- `src/web_app.py`: FastAPI web application for interactive graph simulation and analysis.
- `tests/test_graph.py`: Pytest tests covering costs, MST properties, failure simulation, greedy selection, and reinforcement behavior.
- `data/example_graph.py`: Example power grid graph definitions.
- `templates/`: HTML templates for the web interface.
- `static/`: Static assets (CSS, JavaScript) for the web interface.