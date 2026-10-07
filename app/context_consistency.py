from typing import List


def calculate_context_consistency(
    lines: List[str],
    line_index: int
) -> float:
    """
    Estimate how consistent a line is with the surrounding
    handwritten text.

    Returns a score between 0 and 1.

    This is currently a placeholder heuristic.
    We will replace it with semantic scoring later.
    """

    if not lines:
        return 0.0

    # First/last line has less surrounding context
    if len(lines) == 1:
        return 0.5

    context_score = 0.5

    # If there is text before and after, we have more context
    if line_index > 0:
        context_score += 0.25

    if line_index < len(lines) - 1:
        context_score += 0.25

    return min(context_score, 1.0)