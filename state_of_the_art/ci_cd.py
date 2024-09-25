import os
import subprocess

from state_of_the_art.infrastructure.s3 import S3
from state_of_the_art.config import config


class Docker:
    def build(self):
        os.system(f"docker build -t {config.image_local_tag} .")
        print("Image size", self.image_size())

    def run(self):
        self.docker_stop_all()
        os.system(f"docker run -it --rm -p {config.streamlit_port}:{config.streamlit_port} sota")

    def build_and_run(self):
        self.build()
        self.run()

    def build_and_push(self):
        self.build()
        self.push()

    def docker_stop_all(self):
        os.system("docker stop $(docker ps -a -q)")

    def login(self):
        os.system(f"aws ecr get-login-password --region {config.region} |  docker login --username AWS --password-stdin {config.aws_account_id}.dkr.ecr.{config.region}.amazonaws.com")

    def push(self, image_id=None):
        if not image_id:
            image_id = self.last_image()

        self.add_tag_to_image(image_id)
        os.system(f"docker push '{config.aws_account_id}.dkr.ecr.{config.region}.amazonaws.com/{config.ecr_image}:latest'")

    def add_tag_to_image(self, image_id=None):
        if not image_id:
            image_id = self.last_image()
        os.system(f"docker tag {image_id} '{config.aws_account_id}.dkr.ecr.{config.region}.amazonaws.com/{config.ecr_image}:latest'")

    def last_image(self) -> str:
        result = subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}"', shell=True, text=True)
        result = result.strip()
        return result

    def get_ecr_name(self):
        return f"{config.aws_account_id}.dkr.ecr.{config.region}.amazonaws.com/{config.ecr_image}:latest"

    def image_size(self):
        return subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}: {{.Size}}"', shell=True, text=True)

    def shell_new(self):
        os.system("docker run -it sota /bin/bash")
    
    def local_ip(self, container_id):
        os.system(f"docker inspect -f '{{{{range.NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {container_id}")

class Aws:
    def authentication_profile_str(self):
        return """[profile sota_online]
role_arn = arn:aws:iam::467863034863:user/sota_deployed_role_for_s3
source_profile = sota_deployed_role_for_s3
        """

class Cli:
    def __init__(self):
        self.docker = Docker
        self.s3 = S3
        self.aws = Aws


if __name__ == "__main__":
    import fire
    fire.Fire(Cli)