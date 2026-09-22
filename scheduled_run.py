"""Script pour la Scheduled Task PythonAnywhere : exécute un run et l'enregistre en base.

Commande à configurer dans PythonAnywhere > Tasks :
    python3.13 /home/<votre_user>/<PA_TARGET_DIR>/scheduled_run.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage import save_run
from tester.runner import run_all

if __name__ == "__main__":
    result = run_all()
    run_id = save_run(result)
    print(f"Run #{run_id} enregistré — {result['summary']}")
