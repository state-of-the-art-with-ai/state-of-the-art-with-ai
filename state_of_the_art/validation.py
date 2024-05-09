import os

def run_all():
    print("Starting CI loop")
    current_directory = os.path.dirname(os.path.realpath(__file__))
    parent_directory = os.path.dirname(current_directory)
    print("Base directory: ", parent_directory)

    os.system(f"python -m compileall -q {parent_directory} ")
    os.system(f"cd {parent_directory}; pytest -s ")
    os.system(f"black {parent_directory} ")


if __name__ == "__main__":
    import fire

    fire.Fire()
