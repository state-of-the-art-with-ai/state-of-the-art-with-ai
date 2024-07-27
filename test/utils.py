import os
import socket


def has_internet() -> bool:
    if os.environ.get("NO_INTERNET"):
        return True

    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(2)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        print("Found internet")
        return True
    except socket.error as ex:
        print("No internet found")
        print(ex)
        return False

    return False
