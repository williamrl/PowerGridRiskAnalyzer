from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from src.simulate import run_simulation_to_dict

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
      <head><title>Power Grid Risk Analyzer</title></head>
      <body>
        <h1>Power Grid Risk Analyzer</h1>
        <form method="post">
          <label>Wind strength:
            <input type="number" step="0.1" name="wind" value="7.0">
          </label><br><br>
          <label>Method:
            <select name="method">
              <option value="greedy">Greedy</option>
              <option value="mst">MST</option>
              <option value="none">None</option>
            </select>
          </label><br><br>
          <label>k (number of reinforcements):
            <input type="number" name="k" value="1">
          </label><br><br>
          <input type="submit" value="Run Simulation">
        </form>
      </body>
    </html>
    """


@app.post("/", response_class=HTMLResponse)
def run(wind: float = Form(...), method: str = Form(...), k: int = Form(...)):
    # hard-code example graph 
    results = run_simulation_to_dict("data/example_graph.py", wind, method, k)

    # Very simple HTML rendering
    html = f"""
    <html>
      <head><title>Power Grid Risk Analyzer</title></head>
      <body>
        <h1>Power Grid Risk Analyzer</h1>
        <p><b>Wind:</b> {results['wind']}</p>
        <p><b>Method:</b> {results['method']}</p>
        <p><b>k:</b> {results['k']}</p>
        <p><b>Selected reinforcements:</b> {results['selected']}</p>
        <p><b>Surviving edges ({len(results['surviving'])}):</b> {results['surviving']}</p>
        <p><b>Failed edges ({len(results['failed'])}):</b> {results['failed']}</p>
        <p><b>Blackout zones count:</b> {len(results['blackouts'])}</p>
        <h2>Connected Components</h2>
        <ul>
    """
    for i, comp in enumerate(results["components"], start=1):
        html += f"<li>C{i}: {comp}</li>"
    html += """
        </ul>
        <a href="/">Run another simulation</a>
      </body>
    </html>
    """
    return html
