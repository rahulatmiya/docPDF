# PDF Chatbot

Simple Flask app that extracts text from a PDF and provides a /query endpoint for keyword searches.

Quick start (Windows PowerShell):

1. Create a virtualenv and activate it:

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Place your `sample.pdf` in the project root (or update `.env` to point to another file).

4. Run the app:

```powershell
python app.py
```

5. Query the PDF (example using curl):

```powershell
curl -X POST -H "Content-Type: application/json" -d '{"q":"search term"}' http://localhost:5000/query
```
