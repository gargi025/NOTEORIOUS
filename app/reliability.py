def calculate_reliability(
    ocr_confidence,
    semantic_score,
    kg_consistent,
    domain_consistent
):

    # Prototype weights.
    # These are heuristic and will later be calibrated
    # using evaluation data.

    ocr_weight = 0.45
    semantic_weight = 0.25
    kg_weight = 0.15
    domain_weight = 0.15

    kg_score = 1.0 if kg_consistent else 0.0
    domain_score = 1.0 if domain_consistent else 0.0

    score = (
        ocr_weight * ocr_confidence
        + semantic_weight * semantic_score
        + kg_weight * kg_score
        + domain_weight * domain_score
    )

    # Safety override:
    # A domain conflict must never be automatically accepted.
    if not domain_consistent:
        action = "VERIFY"

    elif score >= 0.80:
        action = "ACCEPT"

    elif score >= 0.60:
        action = "VERIFY"

    else:
        action = "ASK"

    return {
        "score": score,
        "action": action,
        "ocr_confidence": ocr_confidence,
        "semantic_score": semantic_score,
        "kg_consistent": kg_consistent,
        "domain_consistent": domain_consistent,
    }