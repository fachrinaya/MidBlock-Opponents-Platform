"""Their shape: section entry points; shared computation lives in pipeline/."""
from pipeline.sections import get_section_input, extract_section, validate_section

SECTION = "shape"


def get_input(evidence, prior_analysis=None):
    return get_section_input(SECTION, evidence, prior_analysis)


def extract(narrative, evidence, provenance=None):
    return extract_section(SECTION, narrative, evidence, provenance)


def validate(result, evidence):
    return validate_section(SECTION, result, evidence)
