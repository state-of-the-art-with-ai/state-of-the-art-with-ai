import os


def run_all():
    os.system("black . ")
    os.system("pytest")


if __name__ == "__main__":
    import fire

    fire.Fire()
