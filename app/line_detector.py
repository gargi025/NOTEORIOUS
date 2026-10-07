from paddleocr import TextDetection


class TextLineDetector:

    def __init__(self):

        print("Loading PaddleOCR text detector...")

        self.model = TextDetection(
            engine="paddle"
        )

        print("PaddleOCR text detector loaded.")

    def detect(self, image_path):

        output = self.model.predict(
            image_path
        )

        boxes = []

        for result in output:

            data = result.json

            polys = data["res"]["dt_polys"]

            for poly in polys:

                x_coords = [
                    point[0]
                    for point in poly
                ]

                y_coords = [
                    point[1]
                    for point in poly
                ]

                boxes.append(
                    (
                        int(min(x_coords)),
                        int(min(y_coords)),
                        int(max(x_coords)),
                        int(max(y_coords))
                    )
                )

        # Sort top-to-bottom
        boxes.sort(
            key=lambda box: (
                box[1],
                box[0]
            )
        )

        print("\nRAW PADDLE BOXES:")

        for i, box in enumerate(boxes):
            print(f"  {i + 1}: {box}")


        return boxes

    def _merge_wrapped_lines(self, boxes, image_path):

        if len(boxes) <= 1:
            return boxes

        from PIL import Image

        image = Image.open(image_path)
        image_width = image.width

        merged = []

        i = 0

        while i < len(boxes):

            current = boxes[i]

            if i == len(boxes) - 1:
                merged.append(current)
                break

            next_box = boxes[i + 1]

            x1, y1, x2, y2 = current
            nx1, ny1, nx2, ny2 = next_box

            current_width = x2 - x1
            next_width = nx2 - nx1

            # ------------------------------------------------
            # Detect a wrapped continuation line
            # ------------------------------------------------

            current_reaches_right = (
                x2 >= image_width * 0.70
            )

            next_is_short = (
                next_width < current_width * 0.60
            )

            similar_left_margin = (
                abs(nx1 - x1)
                <= image_width * 0.10
            )

            # The next region should be below the current one.
            # Some overlap is expected because PaddleOCR boxes
            # around handwriting can be vertically tall.
            next_is_below = (
                ny1 > y1
            )

            should_merge = (
                current_reaches_right
                and next_is_short
                and similar_left_margin
                and next_is_below
            )

            if should_merge:

                merged_box = (
                    min(x1, nx1),
                    min(y1, ny1),
                    max(x2, nx2),
                    max(y2, ny2)
                )

                merged.append(
                    merged_box
                )

                i += 2

            else:

                merged.append(
                    current
                )

                i += 1

        return merged