import argparse
from configsuite_tui.tui import tui


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="config", type=str, nargs="?", default="")
    parser.add_argument(
        "-c", "--config", type=str, default="", help="Path to config file"
    )
    parser.add_argument("-s", "--schema", type=str, default="", help="Name of schema")

    args = parser.parse_args()
    config = args.config
    schema = args.schema

    tui(config, schema)


if __name__ == "__main__":
    main()
