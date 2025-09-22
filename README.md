csv2rdf: Creates an RDF/S (+just enough OWL) vocabulary definition file based on a CSV file.

## Installation
Best use a virtual environment.

```
$ git clone https://github.com/philbarker/VocabDef.git
$ cd VocabDef
```
[create and activate a virtual environment]
```
(venv) $ pip install .
```

Optional:
To install dependencies used in development only:
```
(venv) $ pip install .[dev] 
```

## Usage: 
```
$ csv2rdf [-h] [-ns <namespace filename>] [-of <output format>] [-v] <terms filename> [<output file>]

Reads term defitions from a CSV file, and converts them to RDF.

positional arguments:
  <terms filename>
  <output file>

options:
  -h, --help            show this help message and exit
  -ns <namespace filename>, --namespace_fn <namespace filename>
  -of <output format>, --output_fmt <output format>
  -v, --version         show program's version number and exit
```

If no namespace filename is supplied then the program will default to namespaces.csv
If no output file is specified then the output will be printed to the terminal
The default output file format is .ttl (Turtle, terse triple language).