import os


def chack_file():
    if not os.path.isfile("/app/storage/data.json"):
        with open("/app/storage/data.json", "x"):
            pass


if __name__ == "__main__":
    chack_file()