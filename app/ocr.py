import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel


MODEL_NAME = "microsoft/trocr-base-handwritten"


class HandwritingRecognizer:

    def __init__(self):
        self.device = (
            "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

        print(f"Loading TrOCR on {self.device}...")

        self.processor = TrOCRProcessor.from_pretrained(
            MODEL_NAME
        )

        self.model = VisionEncoderDecoderModel.from_pretrained(
            MODEL_NAME
        )

        self.model.to(self.device)
        self.model.eval()

        print("TrOCR loaded successfully.")

    def recognize(self, image: Image.Image):

        pixel_values = self.processor(
            images=image,
            return_tensors="pt"
        ).pixel_values

        pixel_values = pixel_values.to(self.device)

        with torch.no_grad():

            output = self.model.generate(
                pixel_values,
                max_new_tokens=64,
                return_dict_in_generate=True,
                output_scores=True
            )

        generated_ids = output.sequences

        text = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True
        )[0].strip()

        # ------------------------------------------------
        # Calculate token-level confidence
        # ------------------------------------------------

        scores = output.scores

        token_confidences = []

        for step, score in enumerate(scores):

            probabilities = torch.softmax(
                score,
                dim=-1
            )

            token_id = generated_ids[
                0,
                step + 1
            ]

            confidence = probabilities[
                0,
                token_id
            ].item()

            token_confidences.append(confidence)

        if token_confidences:
            confidence = sum(token_confidences) / len(
                token_confidences
            )
        else:
            confidence = 0.0

        return {
            "text": text,
            "confidence": confidence,
            "token_confidences": token_confidences
        }


recognizer = None


def recognize_handwriting(image: Image.Image):

    global recognizer

    if recognizer is None:
        recognizer = HandwritingRecognizer()

    return recognizer.recognize(image)