"""Run the whole pipeline in order. ~1 minute (Monte Carlo included)."""
import runpy, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
for step in ["02_build_inputs", "03_demand_model", "04_lca", "05_lcc", "06_ahp", "07_sensitivity", "08_summary"]:
    t = time.time(); print(f"\n=== {step} ===")
    sys.argv = [step]; runpy.run_path(str(HERE / f"{step}.py"), run_name="__main__")
    print(f"    ({time.time()-t:.1f}s)")
