# GraphMind Ultimate — Knowledge Graph & Semantic Reasoning Explorer (Python + Flask)

A full-stack interactive learning workspace for building semantic networks, exploring ontologies, applying inference rules, and asking questions about knowledge graph technology.

## Project Structure

```text
graphmind-python/
├── app.py                # Flask backend, JSON store, inference engine & Q&A API
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── static/
    ├── index.html        # Frontend UI
    ├── styles.css        # Styling
    └── app.js            # Frontend client connected to Flask REST API
```

## Setup & Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd graphmind-python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Python server:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   Visit `http://127.0.0.1:5000`
