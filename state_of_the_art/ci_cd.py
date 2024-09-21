import os
import subprocess
region = 'eu-central-1'
aws_account_id = '467863034863'
streamlit_port = 80
ecr_image = 'sota/monorepo'
image_local_tag = 'sota'
data_bucket = 'sota.data'

class Docker:
    def build(self):
        os.system(f"docker build -t {image_local_tag} .")

    def run(self):
        self.docker_stop_all()
        os.system(f"docker run -it --rm -p {streamlit_port}:{streamlit_port} sota")

    def build_and_run(self):
        self.build()
        self.run()

    def build_and_push(self):
        self.build()
        self.push()

    def docker_stop_all(self):
        os.system("docker stop $(docker ps -a -q)")

    def login(self):
        os.system(f"aws ecr get-login-password --region {region} |  docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.{region}.amazonaws.com")

    def push(self, image_id=None):
        if not image_id:
            image_id = self.last_image()

        self.tag_image(image_id)
        os.system(f"docker push '{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest'")

    def tag_image(self, image_id=None):
        if not image_id:
            image_id = self.last_image()
        os.system(f"docker tag {image_id} '{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest'")

    def last_image(self) -> str:
        result = subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}"', shell=True, text=True)
        result = result.strip()
        return result

    def get_ecr(self):
        return f"{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest"

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

class S3:
    def list_buckets(sel):
        os.system("aws s3api list-buckets")
    
    def list_content(self):
        os.system(f"aws s3 ls s3://{data_bucket}")

    def push_local_data(self):
        os.system(f"aws s3 cp /Users/jean.machado/.tinyws/events s3://{data_bucket}/tinydatawerehouse_events --recursive")

    def pull_data(self, destination="/tmp/pulled_data"):
        os.system(f"aws s3 cp s3://{data_bucket}/tinydatawerehouse_events {destination} --recursive")

class Cli:
    def __init__(self):
        self.docker = Docker
        self.s3 = S3
        self.aws = Aws


if __name__ == "__main__":
    import fire
    fire.Fire(Cli)