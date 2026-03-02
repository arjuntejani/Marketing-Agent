# BrandBrainAI

BrandBrainAI is a starter Python project structure for building brand intelligence and campaign automation workflows.

## Project Structure

```text
BrandBrainAI/
├── analytics/
├── brain/
├── campaigns/
├── extractor/
├── memory/
├── utils/
├── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies from requirements file**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the project**

   ```bash
   python main.py
   ```

## Exact Package Install Commands (Pinned Versions)

Use these commands if you want to install packages category-by-category instead of `requirements.txt`.

### Web scraping

```bash
pip install requests==2.32.3 beautifulsoup4==4.12.3
pip install playwright==1.48.0
python -m playwright install
```

### Local embedding storage

Use ChromaDB by default. FAISS is optional and may not have wheels for all Windows/Python combinations (especially Python 3.13).

```bash
pip install chromadb==0.5.5
# Optional: only if your OS/Python has wheels
# pip install faiss-cpu==1.13.2
```

### Local LLM interface

```bash
pip install llama-cpp-python==0.2.90
```

### File utilities

```bash
pip install python-dotenv==1.0.1 pydantic==2.9.2 tqdm==4.66.5
```

## Notes

- `playwright` is optional but useful for dynamic-page scraping.
- You can keep both `chromadb` and `faiss-cpu` installed, or use only one based on your implementation.


## Windows Compatibility Notes

- If you see NumPy/meson compiler errors while installing dependencies, use Python **3.12** (or 3.11) instead of 3.13.
- Many scientific wheels are not yet consistently available for Python 3.13 on Windows; pip may try to compile from source and fail without Visual Studio Build Tools.
- Recommended: create a new 3.12 venv and reinstall requirements.
