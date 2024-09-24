

from state_of_the_art.ci_cd import S3


class ContainerStartup:
    def setup(self):
        print(f"Setting up container ")
        print("Pulling data from S3")
        for log in S3().pull_data():
            print(log)
        
        print("Downloading ntlk")
        self.download_ntlk()

    def download_ntlk(self):
        print("Downloading ntlk")
        import nltk
        nltk.download("wordnet")


if __name__ == "__main__":
    import fire
    fire.Fire()