import argparse
from configsuite_tui.tui import tui


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="config", type=str, nargs="?", default="")
    parser.add_argument("-s", "--schema", type=str, default="", help="Name of schema")
    return parser


def main():
    arguments = parser()
    args = arguments.parse_args()
    config = args.config
    schema = args.schema

    tui(config, schema)


if __name__ == "__main__":
    main()
