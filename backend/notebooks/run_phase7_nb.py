"""
Execute 06_phase7_model_explainability.ipynb and save outputs.
"""
import nbformat
from nbclient import NotebookClient
import os
import sys
import time

notebook_dir = os.path.dirname(os.path.abspath(__file__))
notebook_path = os.path.join(notebook_dir, "06_phase7_model_explainability.ipynb")

print(f"Reading notebook: {notebook_path}")
nb = nbformat.read(notebook_path, as_version=4)

client = NotebookClient(
    nb,
    timeout=600,
    kernel_name="python3",
    resources={'metadata': {'path': notebook_dir}}
)

print("Executing notebook cells...")
t0 = time.time()
client.execute()
print(f"Execution completed in {time.time() - t0:.2f} seconds.")

with open(notebook_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"Successfully saved executed notebook with outputs: {notebook_path}")
