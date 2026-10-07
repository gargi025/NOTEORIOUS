import re


def extract_relationship(builder, sentence):

    sentence = sentence.strip()

    # X is the [property] from Y
    match = re.match(
        r"^(.*?)\s+is\s+the\s+(.*?)\s+from\s+(?:the\s+)?(.+?)\.?$",
        sentence,
        re.IGNORECASE
    )

    if match:
        return (
            builder.clean_entity(match.group(1)),
            builder.clean_entity(match.group(2) + " from"),
            builder.clean_entity(match.group(3))
        )

    # X revolves around Y / X orbits Y
    match = re.match(
        r"^(.*?)\s+(revolves around|orbits)\s+(.+?)\.?$",
        sentence,
        re.IGNORECASE
    )

    if match:
        return (
            builder.clean_entity(match.group(1)),
            match.group(2).lower(),
            builder.clean_entity(match.group(3))
        )

    # X has Y
    match = re.match(
        r"^(.*?)\s+has\s+(.+?)\.?$",
        sentence,
        re.IGNORECASE
    )

    if match:
        return (
            builder.clean_entity(match.group(1)),
            "has",
            builder.clean_entity(match.group(2))
        )

    # X is Y
    match = re.match(
        r"^(.*?)\s+is\s+(.+?)\.?$",
        sentence,
        re.IGNORECASE
    )

    if match:
        return (
            builder.clean_entity(match.group(1)),
            "is",
            builder.clean_entity(match.group(2))
        )

    return None


def check_kg_consistency(graph, candidate_text, builder):

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

    conflicts = []

    # --------------------------------------------------
    # 1. Check for contradictory existing relationships
    # --------------------------------------------------

    for existing_source, existing_target, data in graph.edges(
        data=True
    ):

        existing_relation = data["relation"]

        if (
            existing_source.lower() == source.lower()
            and existing_relation.lower() == relation.lower()
            and existing_target.lower() != target.lower()
        ):

            conflicts.append(
                {
                    "type": "RELATION_CONFLICT",
                    "source": source,
                    "relation": relation,
                    "candidate_target": target,
                    "existing_target": existing_target
                }
            )

    # --------------------------------------------------
    # 2. Check whether extracted target is already
    #    represented as a meaningful concept in the KG
    # --------------------------------------------------

    graph_nodes_lower = {
        str(node).lower()
        for node in graph.nodes
    }

    if target.lower() not in graph_nodes_lower:

        conflicts.append(
            {
                "type": "UNKNOWN_ENTITY",
                "source": source,
                "relation": relation,
                "candidate_target": target
            }
        )

    return {
        "consistent": len(conflicts) == 0,
        "conflicts": conflicts
    }