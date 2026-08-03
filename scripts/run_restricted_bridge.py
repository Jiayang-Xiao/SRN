#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from restricted_bridge.config import load_config  # noqa: E402
from restricted_bridge.runner import run_experiment  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen-feature restricted SRN bridge.")
    parser.add_argument("--config", required=True, help="YAML experiment configuration")
    parser.add_argument("--output-dir", help="override the configured output directory")
    parser.add_argument(
        "--device", choices=("cpu",), default="cpu",
        help="restricted bridge skeleton currently permits CPU only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        run_experiment(config, args.output_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Restricted bridge preflight failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
