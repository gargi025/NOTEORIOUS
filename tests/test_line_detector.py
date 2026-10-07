from app.line_detector import TextLineDetector


IMAGE_PATH = "data/samples/full_page.jpg"


detector = TextLineDetector()

boxes = detector.detect(IMAGE_PATH)

print(f"\nDetected {len(boxes)} text regions:\n")

for i, box in enumerate(boxes):
    print(f"Line {i + 1}: {box}")