from state_of_the_art.relevance_model.neuralnet import NeuralNetwork
import torch
from typing import List
from sentence_transformers import SentenceTransformer
from state_of_the_art.config import config
import os


class TextEvaluationInference:
    def __init__(self) -> None:
        self.model = NeuralNetwork()
        try:
            self.model.load_state_dict(torch.load(config.TEXT_PREDICTOR_PATH_LOCALLY))
        except Exception as e:
            print(f"Error loading the model for inference: {e}")
            if not os.environ.get("SOTA_TEST"):
                raise e
        self.model.eval()

        self.sentence_transformer = SentenceTransformer("all-mpnet-base-v2")

    def predict(self, text: str) -> int:
        data = torch.from_numpy(self.create_embeddings([text])[0])

        index = torch.argmax(self.model(data)).item()
        return index

    def predict_batch(self, texts: List[str]) -> List[int]:
        data = torch.from_numpy(self.create_embeddings(texts))
        indices = torch.argmax(self.model(data), dim=1).tolist()
        return indices

    def create_embeddings(self, texts: List[str]):
        return self.sentence_transformer.encode(texts)


if __name__ == "__main__":
    import fire

    fire.Fire()
