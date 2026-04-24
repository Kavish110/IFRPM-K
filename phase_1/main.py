"""
NGAFID ML Pipeline — Main Entry Point
Usage:
  python main.py --model cnn --size_ratio 0.1 --debug true
"""

import argparse
import yaml
import os
from utils.seed import set_seed
from utils.logger import get_logger

logger = get_logger("main")


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="NGAFID Production ML Pipeline")
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--dataset", type=str, default=None)
    parser.add_argument("--size_ratio", type=float, default=None)
    parser.add_argument("--model", type=str, choices=["cnn", "conv_mhsa"], default=None)
    parser.add_argument("--debug", type=str, choices=["true", "false"], default=None)
    parser.add_argument("--task", type=str, choices=["train", "explain", "all"], default="all")
    return parser.parse_args()


def apply_overrides(config, args):
    if args.size_ratio is not None:
        config["dataset"]["size_ratio"] = args.size_ratio
    if args.model is not None:
        config["model"]["type"] = args.model
    if args.debug is not None:
        config["dataset"]["debug"] = args.debug.lower() == "true"
    return config


def main():
    args = parse_args()
    config = load_config(args.config)
    config = apply_overrides(config, args)

    set_seed(config["training"].get("seed", 42))

    logger.info("=" * 60)
    logger.info(f"NGAFID Pipeline | Model: {config['model']['type']} | Ratio: {config['dataset']['size_ratio']}")
    logger.info("=" * 60)

    if args.task in ("train", "all"):
        from tasks.train_classification import run as train_run
        train_run(config)

    if args.task in ("explain", "all"):
        from tasks.explain import run as explain_run
        explain_run(config)

    logger.info("Pipeline Execution Finished.")


if __name__ == "__main__":
    main()
