import os

import subprocess
region = 'eu-central-1'
aws_account_id = '467863034863'
ecr_image = 'sota/monorepo'
image_local_tag = 'sota'

def build():
    os.system(f"docker build -t {image_local_tag} .")

def run():
    os.system("docker run -p 5000:5000 sota")

def build_and_run():
    build()
    run()


def login():
    os.system(f"aws ecr get-login-password --region {region} |  docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.{region}.amazonaws.com")

def push(image_id=None):
    if not image_id:
        image_id = last_image()

    tag_image(image_id)
    os.system(f"docker push '{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest'")

def tag_image(image_id=None):
    if not image_id:
        image_id = last_image()
    os.system(f"docker tag {image_id} '{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_image}:latest'")

def last_image() -> str:
    result = subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}"', shell=True, text=True)
    result = result.strip()
    return result

def last_image_size():
    return subprocess.check_output('docker images --filter=reference=sota --format "{{.ID}}: {{.Size}}"', shell=True, text=True)

def shell():
    os.system("docker run -it sota /bin/bash")

if __name__ == "__main__":
    import fire
    fire.Fire()