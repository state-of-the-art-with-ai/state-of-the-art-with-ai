from state_of_the_art.relevance_model.neuralnet import NeuralNetwork
import torch
from typing import List
from sentence_transformers import SentenceTransformer
from state_of_the_art.config import config


class Inference:
    def __init__(self) -> None:
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
        print(f"Using {self.device} device")

        self.model = NeuralNetwork()
        self.model.load_state_dict(torch.load(config.MODEL_LOCALLY))
        self.model.to(self.device)
        self.model.eval()

        self.sentence_transformer = SentenceTransformer("all-mpnet-base-v2")

    def predict(self, text: str) -> int:
        data = torch.from_numpy(self.create_embeddings([text])[0]).to(self.device)

        index = torch.argmax(self.model(data)).item()
        return index

    def create_embeddings(self, texts: List[str]):
        return self.sentence_transformer.encode(texts)
