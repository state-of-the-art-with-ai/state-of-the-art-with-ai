from state_of_the_art.tables.data_sync_table import PushHistory
from state_of_the_art.config import config

import os
import subprocess


class S3:
    def list_buckets(sel):
        os.system("aws s3api list-buckets")

    def list_content(self):
        os.system(f"aws s3 ls s3://{config.data_bucket}")

    def validate_credentials(self):
        if os.path.exists(f"{config.HOME}/.aws/credentials"):
            print("Using credentials from ~/.aws/credentials")
            return

        if os.environ.get("SOTA_TEST"):
            print("Test mode, not validating credentials")
            return
        else:
            print("Using credentials from env variables")

        if not os.environ.get("AWS_ACCESS_KEY_ID"):
            raise Exception("AWS_ACCESS_KEY_ID not set")
        if not os.environ.get("AWS_SECRET_ACCESS_KEY"):
            raise Exception("AWS_SECRET_ACCESS_KEY not set")
        if not os.environ.get("AWS_DEFAULT_REGION"):
            raise Exception("AWS_DEFAULT_REGION not set")

    def push_local_events_data(self):
        self.validate_credentials()
        cmd = f"aws s3 cp {config.TINY_DATA_WAREHOUSE_EVENTS} s3://{config.data_bucket}/tinydatawerehouse_events --recursive"
        if os.environ.get("SOTA_TEST"):
            print(f"Test mode, not pushing to s3 cmd {cmd}")
            return
        else:
            print(f"Actual mode, s3 with command {cmd}")

        p = subprocess.Popen(
            cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        out, error = p.communicate()
        PushHistory().add()
        return out, error

    def pull_events_data(self, destination=None):
        self.validate_credentials()
        if not destination:
            destination = config.TINY_DATA_WAREHOUSE_EVENTS

        yield "Using destination: " + destination

        if os.environ.get("SOTA_TEST"):
            print(f"Test mode, not pulling from s3 cmd {shell_cmd}")
            return

        if not os.path.exists(destination):
            yield subprocess.check_output(
                f"mkdir -p {destination}", shell=True, text=True
            )
        else:
            yield f"Path {destination} already exists skipping creation"

        shell_cmd = f"aws s3 cp s3://{config.data_bucket}/tinydatawerehouse_events {destination} --recursive"

        p = subprocess.Popen(
            shell_cmd,
            shell=True,
            text=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        out, error = p.communicate()
        yield "Error: " + error + "Output: " + out

    def push_model(self):
        shell_cmd = f"aws s3 cp {config.TEXT_PREDICTOR_PATH_LOCALLY} s3://{config.data_bucket}/models/ "
        p = subprocess.Popen(
            shell_cmd,
            shell=True,
            text=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        out, error = p.communicate()
        print("Model pushed to s3")
        return out, error

    def pull_models(self):
        if not os.path.exists(config.MODELS_PATH_LOCALLY):
            os.system("mkdir -p " + config.MODELS_PATH_LOCALLY)

        shell_cmd = f"aws s3 cp {config.MODEL_FOLDER_IN_CLOUD} {config.MODELS_PATH_LOCALLY} --recursive"
        print("Pull command: ", shell_cmd)
        p = subprocess.Popen(
            shell_cmd,
            shell=True,
            text=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        out, error = p.communicate()
        print("Model pushed to s3")
        return out, error
