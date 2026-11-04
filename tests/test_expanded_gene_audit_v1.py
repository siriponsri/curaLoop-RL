import pytest

from research.preparation_v1.expanded_gene_audit import operation, project


def test_expanded_discovery_is_identifier_only_and_batch_metadata_only():
    assert (
        operation("https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/target/genesymbol/CA2/aids/JSON")
        == "gene_aids"
    )
    assert (
        operation("https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1,2/description/JSON")
        == "batch_descriptions"
    )
    assert project("gene_aids", {"IdentifierList": {"AID": [2, 1, 2]}}) == [1, 2]


@pytest.mark.parametrize(
    "url",
    [
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/target/genesymbol/CA2/aids/JSON?aids_type=active",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1,2/concise/JSON",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1,2/record/JSON",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/cids/JSON?cids_type=inactive",
    ],
)
def test_expansion_does_not_open_outcome_or_filtered_membership_routes(url):
    with pytest.raises(ValueError):
        operation(url)


def test_every_batch_member_is_checked_for_unexpected_outcome_data():
    payload = {
        "PC_AssayContainer": [
            {"assay": {"descr": {"name": "metadata"}}},
            {"assay": {"descr": {}, "data": [{"active": True}]}},
        ]
    }
    with pytest.raises(ValueError, match="data section"):
        project("batch_descriptions", payload)
