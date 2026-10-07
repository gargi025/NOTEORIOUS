import re


# ---------------------------------------------------------
# Solar System prototype knowledge
# ---------------------------------------------------------

KNOWN_ENTITIES = {
    "sun",
    "earth",
    "moon",
    "mars",
    "star",
}


EXPECTED_RELATIONS = {
    ("sun", "is", "star"),
    ("earth", "third planet from", "sun"),
    ("earth", "revolves around", "sun"),
    ("earth", "has", "moon"),
    ("mars", "fourth planet from", "sun"),
}


def normalize(text):
    text = text.strip().lower()
    text = re.sub(r"^(the|a|an)\s+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def check_domain_consistency(
    graph,
    candidate_text,
    builder
):
    """
    Check whether the relationship extracted from a
    candidate sentence is compatible with the prototype's
    Solar System domain knowledge.
    """

    from app.kg_consistency import extract_relationship

    relationship = extract_relationship(
        builder,
        candidate_text
    )

    if relationship is None:
        return {
            "consistent": True,
            "conflicts": []
        }

    source, relation, target = relationship

    source = normalize(source)
    relation = normalize(relation)
    target = normalize(target)

    conflicts = []

    # -----------------------------------------------------
    # Check whether entities belong to the known domain
    # -----------------------------------------------------

    if source not in KNOWN_ENTITIES:

        conflicts.append({
            "type": "UNKNOWN_SOURCE",
            "source": source,
            "relation": relation,
            "target": target
        })

    if target not in KNOWN_ENTITIES:

        conflicts.append({
            "type": "UNKNOWN_TARGET",
            "source": source,
            "relation": relation,
            "target": target
        })

    # -----------------------------------------------------
    # Check expected relationship
    # -----------------------------------------------------

    if (
        source in KNOWN_ENTITIES
        and target in KNOWN_ENTITIES
    ):

        expected = (
            source,
            relation,
            target
        )

        if expected not in EXPECTED_RELATIONS:

            conflicts.append({
                "type": "DOMAIN_RELATION_CONFLICT",
                "source": source,
                "relation": relation,
                "target": target
            })

    return {
        "consistent": len(conflicts) == 0,
        "conflicts": conflicts
    }
