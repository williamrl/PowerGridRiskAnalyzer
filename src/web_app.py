from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.simulate import run_simulation_to_dict, load_graph_from_py, load_graph_from_json
import base64
from pathlib import Path

app = FastAPI()

# mount a `static` directory (create if needed)
static_dir = Path(__file__).resolve().parents[1] / "static"
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Render a simple form
    return templates.TemplateResponse("index.html", {"request": request, "default_wind": 7.0})

from fastapi import UploadFile, File
import json
import tempfile
import os

@app.post("/", response_class=HTMLResponse)
async def run(request: Request, wind: float = Form(...), method: str = Form('greedy'), k: int = Form(1), dataset: str = Form(None), generators: str = Form(None), upload: UploadFile = File(None)):
    # run simulation against the example python graph module
    # If the user uploaded a JSON graph file, save it to a temp file and pass the path
    temp_path = None
    try:
        if upload is not None and upload.filename:
            content = await upload.read()
            # validate JSON
            json.loads(content.decode('utf-8'))
            tf = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            tf.write(content)
            tf.flush()
            tf.close()
            temp_path = tf.name
            file_path = temp_path
        else:
            file_path = dataset or 'data/example_graph.py'

        gens = None
        if generators:
            gens = [g.strip() for g in generators.split(',') if g.strip()]

        results = run_simulation_to_dict(file_path, wind=wind, method=method, k=k, generators=gens)
        # plot generation not yet implemented
        plot_data = None
    finally:
        # cleanup temp file if created
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
    # Provide both the raw results dict and common keys for older templates
    context = {
        "request": request,
        "results": results,
        "wind": wind,
        "method": method,
        "k": k,
        "reinforcements": k,
        "selected": results.get("selected"),
        "surviving": results.get("surviving"),
        "failed": results.get("failed"),
        "blackouts": results.get("blackouts"),
        "components": results.get("components"),
        "plot_data": plot_data,
    }
    return templates.TemplateResponse("results.html", context)
