"""CLI for miaosuan-bazi-engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import computeFromBirth


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute deterministic BaZi facts from birth data.")
    parser.add_argument("--input", required=True, help="Path to a birth input JSON file.")
    parser.add_argument("--ruleset", help="Optional path to a custom ruleset JSON file.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = computeFromBirth(payload, ruleset_path=args.ruleset)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
