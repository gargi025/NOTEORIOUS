from PIL import Image

from app.ocr import recognize_handwriting


def test_ocr():
    image = Image.new(
        "RGB",
        (1000, 400),
        "white",
    )

    text = recognize_handwriting(image)

    assert isinstance(text, str)