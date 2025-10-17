import pytest
from csv2rdf import csv2rdfConverter
from rdflib import Graph, URIRef, Literal
from rdflib import DCTERMS, OWL, RDF, RDFS, SDO, SKOS, XSD
from rdflib import compare

namespaces_fn = "tests/data/namespaces.csv"
input_csv_fn = "tests/data/terms.csv"
output_fn = "tests/data/terms.ttl"
skos_csv_fn = "tests/data/concepts.csv"
skos_output_fn = "tests/data/concepts.ttl"


@pytest.fixture(scope="function")
def test_Converter():
    converter = csv2rdfConverter()
    return converter


@pytest.fixture(scope="module")
def rdfs_Converter():
    converter = csv2rdfConverter()
    return converter


@pytest.fixture(scope="module")
def skos_converter():
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


def test_process_type(test_Converter):
    c = test_Converter
    assert c.process_type("Concept") == SKOS.Concept
    assert c.process_type("Property") == RDF.Property
    assert c.process_type("Class") == RDFS.Class
    with pytest.raises(ValueError) as e:
        c.process_type("Wrong")
    assert str(e.value) == "Unknown term type Wrong."


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
    with pytest.warns(UserWarning, match="Cannot convert column Wrong un to RDF term."):
        c.check_keys(keys)

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
    keys = [  # these are common keys for SKOS
        "Type",
        "URI",
        "Label",
        "Definition",
        "Notation",
        "Related term",
        "Relationship",
    ]
    assert c.check_keys(keys)

def test_process_term(test_Converter):
    c= test_Converter
    c.add_namespace("ex", "https://example.org/terms#")
    cURI = "ex:test"
    termRef = c.process_term(cURI)
    assert termRef == URIRef("https://example.org/terms#test")
    cURI = "ex:"
    termRef = c.process_term(cURI)
    assert termRef == URIRef("https://example.org/terms#")
    cURI = "ex"
    with pytest.raises(ValueError) as e:
        termRef = c.process_term(cURI)
    assert str(e.value) == "ex does not seem to be a curie."




def test_convert_row_rdfs(test_Converter):
    c = test_Converter
    c.add_namespace("ex", "https://example.org/terms#")
    c.add_namespace("xsd", "http://www.w3.org/2001/XMLSchema#")
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
        "Domain Includes": "ex:Document, ex:File ",
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


def test_convert_row_skos(test_Converter):
    c = test_Converter
    c.add_namespace("ex", "https://example.org/concepts#")
    c.add_namespace("xsd", "http://www.w3.org/2001/XMLSchema#")
    row1 = {
        "Type": "Concept Scheme",
        "URI": "ex:Example",
        "Label": "Example Concept Scheme",
        "Notation": " ",
        "Definition": "An example concept scheme.",
        "Related term": "ex:Document, ex:File ",
        "Relationship": "hasTopConcept",
    }
    c.convert_row(row1)
    csRef = URIRef("https://example.org/concepts#Example")
    DocRef = URIRef("https://example.org/concepts#Document")
    FileRef = URIRef("https://example.org/concepts#File")
    assert ((csRef, RDF.type, SKOS.ConceptScheme)) in c.vocab_rdf
    assert ((csRef, DCTERMS.title, Literal("Example Concept Scheme"))) in c.vocab_rdf
    assert (
        (csRef, DCTERMS.description, Literal("An example concept scheme."))
    ) in c.vocab_rdf
    assert ((csRef, SKOS.hasTopConcept, DocRef)) in c.vocab_rdf
    assert ((csRef, SKOS.hasTopConcept, FileRef)) in c.vocab_rdf
    assert ((csRef, SKOS.notation, None)) not in c.vocab_rdf
    row2 = {
        "Type": "Concept",
        "URI": "ex:ExampleConcept",
        "Label": "Example Concept",
        "Notation": "Ex1",
        "Definition": "An example concept.",
        "Related term": "ex:Example ",
        "Relationship": "topConceptOf, inScheme",
    }
    c.convert_row(row2)
    print(c.vocab_rdf.serialize())
    cRef = URIRef("https://example.org/concepts#ExampleConcept")
    assert (cRef, RDF.type, SKOS.Concept) in c.vocab_rdf
    assert (cRef, SKOS.prefLabel, Literal("Example Concept")) in c.vocab_rdf
    assert (cRef, SKOS.definition, Literal("An example concept.")) in c.vocab_rdf
    assert (cRef, SKOS.notation, Literal("Ex1")) in c.vocab_rdf
    assert (cRef, SKOS.topConceptOf, csRef) in c.vocab_rdf
    assert (cRef, SKOS.inScheme, csRef) in c.vocab_rdf


def test_read_csv(rdfs_Converter):
    c = rdfs_Converter
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


def test_read_skos_csv(skos_converter):
    sc = skos_converter
    sc.read_namespaces(namespaces_fn)
    sc.read_csv(skos_csv_fn)


#  uncomment the method below to write a new expected graph for future tests
# def test_write_out(test_Converter):
#    c = test_Converter
#    c.write_out(output_fn)
#
# def test_write_out(skos_converter):
#    c = skos_converter
#    c.write_out(skos_output_fn)


def test_rdfs_conversion(rdfs_Converter):
    c = rdfs_Converter
    expected_g = Graph()
    expected_g.parse(output_fn)
    print(c.vocab_rdf.serialize(format="turtle"))
    assert compare.isomorphic(c.vocab_rdf, expected_g)


def test_skos_conversion(skos_converter):
    c = skos_converter
    expected_g = Graph()
    expected_g.parse(skos_output_fn)
    print(c.vocab_rdf.serialize(format="turtle"))
    assert compare.isomorphic(c.vocab_rdf, expected_g)

    
