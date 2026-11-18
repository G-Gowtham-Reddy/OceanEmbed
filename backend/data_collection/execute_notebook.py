"""
Execute the Phase 4 Preprocessing Notebook and save all executed outputs.
"""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK_PATH = NOTEBOOK_DIR / "01_phase4_data_preprocessing.ipynb"

print(f"Reading notebook: {NOTEBOOK_PATH.name}...")
with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(NOTEBOOK_DIR)}})

print("Executing all cells in notebook...")
client.execute()

print("Writing executed notebook with cell outputs...")
with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"[SUCCESS] Notebook executed and updated at: {NOTEBOOK_PATH.resolve()}")
