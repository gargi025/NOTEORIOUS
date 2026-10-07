import re


def normalize_ocr_text(text):
    text = text.strip()

    # Remove obvious OCR artifacts at the beginning
    text = re.sub(r"^[#*_]+", "", text).strip()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # Remove trailing OCR dashes
    text = re.sub(r"[-–—]+$", "", text).strip()

    return text


def merge_logical_lines(lines):
    """
    Convert physical OCR lines into logical sentences.

    Example:
        ["the third planet from the", "sun."]
        ->
        ["the third planet from the sun."]
    """

    merged = []
    current = ""

    for raw_line in lines:
        line = normalize_ocr_text(raw_line)

        if not line:
            continue

        if not current:
            current = line
            continue

        # Previous physical line has not ended a sentence.
        if not re.search(r"[.!?]$", current):
            current = current + " " + line
        else:
            merged.append(current)
            current = line

    if current:
        merged.append(current)

    return merged