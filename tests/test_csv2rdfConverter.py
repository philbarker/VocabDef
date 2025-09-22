import pytest
from csv2rdf import csv2rdfConverter
from rdflib import Graph, URIRef, Literal
from rdflib import OWL, RDF, RDFS, SDO, SKOS, XSD
from rdflib import compare

namespaces_fn = "tests/data/namespaces.csv"
input_csv_fn = "tests/data/terms.csv"
output_fn = "tests/data/terms.ttl"


@pytest.fixture(scope="module")
def test_Converter():
    converter = csv2rdfConverter()
    return converter


@pytest.fixture(scope="module")
def example_Converter():
    converter = csv2rdfConverter()
    return converter


def test_init(test_Converter):
    c = test_Converter
    g = Graph()
    assert c.vocab_rdf.serialize() == g.serialize()


def test_read_namespaces(test_Converter):
    c = test_Converter
    c.read_namespaces(namespaces_fn)
    assert c.namespaces["ex"] == "https://example.org/terms#"


def test_check_keys(test_Converter):
    c = test_Converter

    keys = [
        "Type",  # maps to rdfs:type,
        "URI",  # maps to URIRef
        "Label",  # maps to rdfs:label
        "Comment",  # maps to rdfs:comment
        "Usage Note",  # maps to skos:usageNote
        "Domain Includes",  # maps to sdo.domainIncludes
        "Range Includes",  # maps to sdo.rangeIncludes
        "Wrong un",
    ]
    with pytest.raises(ValueError) as e:
        c.check_keys(keys)
    assert str(e.value) == "Cannot convert Wrong un to RDF term."

    keys = []
    with pytest.raises(ValueError) as e:
        c.check_keys(keys)
    assert str(e.value) == "Must have columns for Type and URI in the input csv."
    keys = ["URI"]
    with pytest.raises(ValueError) as e:
        c.check_keys(keys)
    assert str(e.value) == "Must have columns for Type and URI in the input csv."
    keys = ["Type"]
    with pytest.raises(ValueError) as e:
        c.check_keys(keys)
    assert str(e.value) == "Must have columns for Type and URI in the input csv."


def test_convert_row(test_Converter):
    c = test_Converter
    row = {"Type": "Property", "URI": "p:createdDateTime"}
    with pytest.raises(ValueError) as e:
        c.convert_row(row)
    assert str(e.value) == "Prefix p does not correspond to a known namespace."
    row = {
        "Type": "Property",
        "URI": "ex:createdDateTime",
        "Label": "Created Date Time",
        "Comment": "The date and Time stamp when the Resource was created.",
        "Usage Note": "Should be xsd:dateTime format.",
        "Domain Includes": "ex:Document, ex:File",
        "Range Includes": "xsd:dateTime",
    }
    c.convert_row(row)
    assert ("ex", URIRef("https://example.org/terms#")) in c.vocab_rdf.namespaces()
    dtRef = URIRef("https://example.org/terms#createdDateTime")
    DocRef = URIRef("https://example.org/terms#Document")
    FileRef = URIRef("https://example.org/terms#File")
    assert ((dtRef, RDF.type, RDF.Property)) in c.vocab_rdf
    assert ((dtRef, RDFS.label, Literal("Created Date Time"))) in c.vocab_rdf
    assert (
        (
            dtRef,
            RDFS.comment,
            Literal("The date and Time stamp when the Resource was created."),
        )
    ) in c.vocab_rdf
    assert (
        (dtRef, SKOS.note, Literal("Should be xsd:dateTime format."))
    ) in c.vocab_rdf
    assert ((dtRef, SDO.domainIncludes, DocRef)) in c.vocab_rdf
    assert ((dtRef, SDO.domainIncludes, FileRef)) in c.vocab_rdf
    assert ((dtRef, SDO.rangeIncludes, XSD.dateTime)) in c.vocab_rdf


def test_read_csv(example_Converter):
    c = example_Converter
    c.read_namespaces(namespaces_fn)
    c.read_csv(input_csv_fn)
    ontRef = URIRef("https://example.org/terms#")
    assert ((ontRef, RDF.type, OWL.Ontology)) in c.vocab_rdf
    assert ((ontRef, RDFS.label, Literal("Test Terms"))) in c.vocab_rdf
    assert (
        (
            ontRef,
            RDFS.comment,
            Literal("A test RDF vocabulary."),
        )
    ) in c.vocab_rdf


#  uncomment the method below to write a new expected graph for future tests
# def test_write_out(test_Converter):
#    c = test_Converter
#    c.write_out(output_fn)


def test_conversion(example_Converter):
    c = example_Converter
    expected_g = Graph()
    expected_g.parse(output_fn)
    print(c.vocab_rdf.serialize(format="turtle"))
    assert compare.isomorphic(c.vocab_rdf, expected_g)
