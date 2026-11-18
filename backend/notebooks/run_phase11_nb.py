import nbformat
from nbclient import NotebookClient
import os
import sys

def run_notebook():
    nb_path = "backend/notebooks/10_phase11_land_sea_masking_and_ocean_boundary_validation.ipynb"
    print(f"Executing {nb_path}...")
    
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
        
    client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": "backend/notebooks"}})
    client.execute()
    
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
        
    print(f"Execution complete. Output saved to {nb_path}")

if __name__ == "__main__":
    run_notebook()
