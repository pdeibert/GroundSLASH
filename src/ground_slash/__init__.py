__version__ = "0.0.0.dev0"
__author__ = "Philipp Deibert"

from .debug import debug  # noqa


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="GroundSLASH",
        description="Parser & grounder for the SLASH input language",
    )
    parser.add_argument("-f", "--file", type=str, default=None)
    parser.add_argument("-o", "--outfile", type=str, default=None)

    # parse command line arguments
    args = parser.parse_args()

    if args.file is None:
        print("Missing value for option '-f'/'--file' for command 'ground'")
        sys.exit(1)

    from .grounding import Grounder
    from .program import Program

    # read input
    with open(args.file, "r") as f:
        prog = Program.from_string(f.read())

    # ground program
    ground_prog = Grounder(prog).ground()

    if args.outfile is None:
        # output ground program to console
        print(ground_prog)
    else:
        # write ground program to specified output file
        with open(args.outfile, "w") as f:
            f.write(str(ground_prog))

    sys.exit(0)
