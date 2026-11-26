"""Build the interactive calculator from output/params.json (run 01_return_model.py first).

python3 -I scripts/02_build_calculator.py
  -> output/calculator.html           standalone page
  -> output/calculator_fragment.html  same page without <html>/<head> (for hosts that add their own)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
params = json.loads((ROOT / "output" / "params.json").read_text())
page = Path(__file__).with_name("calculator_template.html").read_text().replace("__PARAMS__", json.dumps(params))
(ROOT / "output" / "calculator_fragment.html").write_text(page)
(ROOT / "output" / "calculator.html").write_text(
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'
    + page + "\n</body>\n</html>\n")
print("wrote output/calculator.html")
