"""Nutmeg run entry: save the complete offline rebuild in the recorded output dir."""
import os
from pathlib import Path
import sys

sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

if __name__=="__main__":
    from run import main
    sys.argv=["run.py","demo","--workspace",os.environ["NUTMEG_OUTPUT_DIR"]]
    main()
