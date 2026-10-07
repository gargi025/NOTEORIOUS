from PIL import Image

from app.ocr import recognize_handwriting


image = Image.open(
    "data/samples/because_line.png"
).convert("RGB")


result = recognize_handwriting(image)


print("\nTrOCR result:")
print("Text:", result["text"])
print("Confidence:", result["confidence"])

print("\nToken confidences:")

for confidence in result["token_confidences"]:
    print(f"{confidence:.4f}")