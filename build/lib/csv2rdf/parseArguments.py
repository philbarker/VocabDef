from argparse import ArgumentParser
from ._version import __version__

# defaults
termsCSV_fn = "terms.csv"
namespace_fn = "namespaces.csv"
# aboutFileName = "about.csv"
output_fmt = "turtle"

def parse_arguments():
    parser = ArgumentParser(
        prog="csv2rdf.py",
        description="Reads term defitions from a CSV file, and converts them to RDF.",
    )
    parser.add_argument("termsCSV_fn", type=str, metavar="<terms filename>")
    parser.add_argument(
        "-ns",
        "--namespace_fn",
        type=str,
        metavar="<namespace filename>",
        default=namespace_fn,
    )
    parser.add_argument(
        "output_fn",
        nargs="?",
        type=str,
        metavar="<output file>",
    )
    parser.add_argument(
        "-of",
        "--output_fmt",
        type=str,
        metavar="<output format>",
        default=output_fmt,
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )
    return parser.parse_args()