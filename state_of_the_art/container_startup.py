

from state_of_the_art.infrastructure.s3 import S3


class ContainerStartup:
    def __init__(self) -> None:
        self.pull_models = S3().pull_models
        self.pull_events_data = S3().pull_events_data
    def setup(self):
        print(f"Setting up container ")
        print("Pulling data from S3")
        for log in self.pull_events_data():
            print(log)
        
        print("Downloading ntlk")
        self.download_ntlk()

        self.pull_models()

    def download_ntlk(self):
        print("Downloading ntlk")
        import nltk
        nltk.download("wordnet")


if __name__ == "__main__":
    import fire
    fire.Fire()