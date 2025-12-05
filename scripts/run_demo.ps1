# Activate virtualenv (PowerShell)
. .\.venv\Scripts\Activate.ps1
# Install dependencies (first-time)
python -m pip install -r requirements.txt
# Run the app
python -m uvicorn src.web_app:app --reload --port 8000
