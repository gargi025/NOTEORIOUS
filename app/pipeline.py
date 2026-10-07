from PIL import Image

from app.line_detector import TextLineDetector
from app.ocr import recognize_handwriting
from app.reliability import calculate_reliability
from app.knowledge import KnowledgeGraphBuilder
from app.semantic_consistency import calculate_semantic_consistency
from app.kg_consistency import check_kg_consistency
from app.text_merger import merge_logical_lines
from app.domain_consistency import check_domain_consistency


class HandwritingPipeline:

    def __init__(self):

        self.detector = TextLineDetector()

        self.knowledge_builder = (
            KnowledgeGraphBuilder()
        )

    def process(self, image_path):

        image = Image.open(image_path).convert("RGB")

        # --------------------------------------------------
        # 1. Detect physical text regions
        # --------------------------------------------------

        boxes = self.detector.detect(image_path)

        crops = []
        recognized_lines = []

        # --------------------------------------------------
        # 2. OCR each physical region
        # --------------------------------------------------

        for box in boxes:

            x1, y1, x2, y2 = box

            padding_x = 80
            padding_y = 40

            image_width, image_height = image.size

            x1 = max(0, x1 - padding_x)
            y1 = max(0, y1 - padding_y)
            x2 = min(image_width, x2 + padding_x)
            y2 = min(image_height, y2 + padding_y)

            crop = image.crop(
                (x1, y1, x2, y2)
            )

            ocr_result = recognize_handwriting(crop)

            recognized_lines.append(
                ocr_result["text"]
            )

            crops.append(
                (box, crop, ocr_result)
            )

        # --------------------------------------------------
        # 3. Reconstruct logical sentences
        # --------------------------------------------------

        logical_sentences = merge_logical_lines(
            recognized_lines
        )

        # --------------------------------------------------
        # 4. Build KG from logical sentences
        # --------------------------------------------------

        knowledge_graph = self.knowledge_builder.build(
            logical_sentences
        )

        # --------------------------------------------------
        # 5. Reliability analysis
        # --------------------------------------------------

        results = []

        for i, sentence in enumerate(logical_sentences):

            context_lines = [
                text
                for j, text in enumerate(logical_sentences)
                if j != i
            ]

            context = " ".join(context_lines)

            semantic_score = calculate_semantic_consistency(
                sentence,
                context
            )

            kg_result = check_kg_consistency(
                knowledge_graph,
                sentence,
                self.knowledge_builder
            )

            domain_result = check_domain_consistency(
                knowledge_graph,
                sentence,
                self.knowledge_builder
            )

            # For now, use sentence-level confidence.
            # We will improve aggregation later.
            confidence = 0.0

            if i < len(crops):
                confidence = crops[i][2]["confidence"]

            reliability = calculate_reliability(
                ocr_confidence=confidence,
                semantic_score=semantic_score,
                kg_consistent=kg_result["consistent"],
                domain_consistent=domain_result["consistent"]
            )

            results.append(
                {
                    "line_number": i + 1,
                    "text": sentence,
                    "confidence": confidence,
                    "semantic_score": semantic_score,

                    "kg_consistent": kg_result["consistent"],
                    "kg_conflicts": kg_result["conflicts"],

                    "domain_consistent": domain_result["consistent"],
                    "domain_conflicts": domain_result["conflicts"],

                    "reliability_score": reliability["score"],
                    "action": reliability["action"],
                }
            )

        return {
            "lines": results,
            "graph": knowledge_graph,
            "physical_lines": recognized_lines,
            "logical_sentences": logical_sentences,
        }