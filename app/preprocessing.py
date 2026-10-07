from PIL import Image, ImageOps
import cv2
import numpy as np


def load_image(image_file) -> Image.Image:
    """Load an uploaded image and correct its orientation."""

    image = Image.open(image_file)
    image = ImageOps.exif_transpose(image)

    return image.convert("RGB")


def remove_horizontal_lines(image: Image.Image) -> Image.Image:
    """
    Remove notebook/page ruling using morphological operations.
    """

    image_np = np.array(image)

    gray = cv2.cvtColor(
        image_np,
        cv2.COLOR_RGB2GRAY,
    )

    # Detect dark horizontal lines.
    binary = cv2.threshold(
        gray,
        180,
        255,
        cv2.THRESH_BINARY_INV,
    )[1]

    # A wide horizontal kernel detects notebook ruling.
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (40, 1),
    )

    horizontal_lines = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        horizontal_kernel,
    )

    # Remove detected lines from the image.
    cleaned = cv2.inpaint(
        gray,
        horizontal_lines,
        3,
        cv2.INPAINT_TELEA,
    )

    return Image.fromarray(cleaned)


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepare a handwritten note for line detection/OCR.
    Handles both RGB and grayscale images.
    """

    image_np = np.array(image)

    # If image is already grayscale, don't convert it again.
    if len(image_np.shape) == 2:
        gray = image_np

    elif len(image_np.shape) == 3:
        gray = cv2.cvtColor(
            image_np,
            cv2.COLOR_RGB2GRAY,
        )

    else:
        raise ValueError(
            f"Unsupported image shape: {image_np.shape}"
        )

    # Resize very large images.
    height, width = gray.shape
    max_dimension = 1800

    if max(height, width) > max_dimension:

        scale = max_dimension / max(height, width)

        new_width = int(width * scale)
        new_height = int(height * scale)

        gray = cv2.resize(
            gray,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

    # Improve local contrast.
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    # Mild denoising.
    denoised = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0,
    )

    return Image.fromarray(denoised)

def detect_text_lines(image: Image.Image):
    """
    Detect individual handwriting lines using connected components.

    The idea is:
    1. Threshold the handwriting.
    2. Find connected handwriting components.
    3. Group components whose vertical positions belong
       to the same writing line.
    4. Crop each detected line.
    """

    image_np = np.array(image)

    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(
            image_np,
            cv2.COLOR_RGB2GRAY,
        )
    else:
        gray = image_np

    # Convert dark handwriting to white foreground.
    binary = cv2.threshold(
        gray,
        180,
        255,
        cv2.THRESH_BINARY_INV,
    )[1]

    # Remove tiny noise.
    kernel = np.ones((2, 2), np.uint8)

    binary = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        kernel,
    )

    # Find connected components.
    num_labels, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8,
        )
    )

    components = []

    for i in range(1, num_labels):

        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]

        # Ignore tiny noise.
        if area < 8:
            continue

        # Ignore extremely large objects.
        if w > gray.shape[1] * 0.9:
            continue

        if h > gray.shape[0] * 0.5:
            continue

        components.append(
            {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "center_y": y + h / 2,
                "area": area,
            }
        )

    if not components:
        return []

    # Estimate typical character height.
    heights = [
        component["h"]
        for component in components
    ]

    median_height = float(
        np.median(heights)
    )

    # Sort components from top to bottom.
    components.sort(
        key=lambda component: component["center_y"]
    )

    # Group components into handwriting lines.
    lines = []

    for component in components:

        assigned = False

        component_center = component["center_y"]

        for line in lines:

            line_center = line["center_y"]

            # Components within roughly one character height
            # belong to the same handwriting line.
            tolerance = max(
                12,
                median_height * 0.8,
            )

            if abs(
                component_center - line_center
            ) <= tolerance:

                line["components"].append(
                    component
                )

                # Recalculate line center.
                line["center_y"] = np.mean(
                    [
                        c["center_y"]
                        for c in line["components"]
                    ]
                )

                assigned = True
                break

        if not assigned:

            lines.append(
                {
                    "center_y": component_center,
                    "components": [component],
                }
            )

    # Sort lines top-to-bottom.
    lines.sort(
        key=lambda line: line["center_y"]
    )

    detected_lines = []

    for line in lines:

        components_in_line = line[
            "components"
        ]

        if not components_in_line:
            continue

        # Determine bounding box of entire line.
        x1 = min(
            c["x"]
            for c in components_in_line
        )

        y1 = min(
            c["y"]
            for c in components_in_line
        )

        x2 = max(
            c["x"] + c["w"]
            for c in components_in_line
        )

        y2 = max(
            c["y"] + c["h"]
            for c in components_in_line
        )

        # Add padding.
        x_padding = 20
        y_padding = 20

        x1 = max(
            0,
            x1 - x_padding,
        )

        y1 = max(
            0,
            y1 - y_padding,
        )

        x2 = min(
            gray.shape[1],
            x2 + x_padding,
        )

        y2 = min(
            gray.shape[0],
            y2 + y_padding,
        )

        line_image = gray[
            y1:y2,
            x1:x2,
        ]

        # Ignore extremely small detections.
        if (
            line_image.shape[1] < 30
            or line_image.shape[0] < 10
        ):
            continue

        detected_lines.append(
            Image.fromarray(
                line_image
            ).convert("RGB")
        )

    return detected_lines


def preprocess_for_ocr(image_file):
    """
    Complete preprocessing pipeline.

    Returns:
        original_image
        processed_image
        text_lines
    """

    original_image = load_image(
        image_file
    )

    # Remove notebook ruling first.
    without_lines = remove_horizontal_lines(
        original_image
    )

    processed_image = preprocess_image(
        without_lines
    )

    text_lines = detect_text_lines(
        processed_image
    )

    return (
        original_image,
        processed_image,
        text_lines,
    )