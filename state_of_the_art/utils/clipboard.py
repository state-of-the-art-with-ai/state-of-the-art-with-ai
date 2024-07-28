def get_clipboard_content() -> str:
    import subprocess

    return subprocess.check_output("clipboard get_content", shell=True, text=True)
