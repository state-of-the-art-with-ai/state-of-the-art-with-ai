import os
import subprocess
region = 'eu-central-1'
aws_account_id = '467863034863'
streamlit_port = 80
ecr_image = 'sota/monorepo'
image_local_tag = 'sota'

class Docker:
    def build(self):
        os.system(f"docker build -t {image_local_tag} .")

    def run(self):
        self.docker_stop_all()
        os.system(f"docker run -it --rm -p {streamlit_port}:{streamlit_port} sota")

    def build_and_run(self):
        self.build()
        self.run()

    def docker_stop_all(self):
        os.system("docker stop $(docker ps -a -q)")

    def login(self):
        os.system(f"aws ecr get-login-password --region {region} |  docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.{region}.amazonaws.com")

    def push(self, image_id=None):
        if not image_id:
            image_id = last_image()

        self.tag_image(image_id)
        os.system(f"docker push '{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest'")

    def tag_image(self, image_id=None):
        if not image_id:
            image_id = last_image()
        os.system(f"docker tag {image_id} '{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest'")

    def last_image(self) -> str:
        result = subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}"', shell=True, text=True)
        result = result.strip()
        return result

    def get_ecr(self):
        return f"{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest"

    def last_image_size(self):
        return subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}: {{.Size}}"', shell=True, text=True)

    def shell(self):
        os.system("docker run -it sota /bin/bash")

class Cli:
    def __init__(self):
        self.docker = Docker()

if __name__ == "__main__":
    import fire
    fire.Fire(Cli)