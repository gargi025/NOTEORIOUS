from PIL import Image
import numpy as np

from app.preprocessing import preprocess_image


def test_preprocessing():
    # Create a dummy white image
    image = Image.fromarray(
        np.ones((500, 800, 3), dtype=np.uint8) * 255
    )

    processed = preprocess_image(image)

    assert processed.mode == "RGB"
    assert processed.width > 0
    assert processed.height > 0