#!/usr/bin/env python
from csv2rdf import csv2rdfConverter, parse_arguments, __version__


def main():
    args = parse_arguments()
    c = csv2rdfConverter()
    c.read_namespaces(args.namespace_fn)
    c.read_csv(args.termsCSV_fn)
    c.write_out(args.output_fn, args.output_fmt)


if __name__ == "__main__":
    main()