import os
import time
import shutil
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SOURCE = r"D:\Files\Downloads"

RULES = {
    "pdsk": r"D:\Kuliah\PDSK",
    "so": r"D:\Kuliah\SOperasi",
    "uh": r"D:\Kuliah\UHadist",
    "alin": r"D:\Kuliah\ALIN",
    "meme": r"D:\Files\Pictures\meme",
    "nsfw": r"D:\Files\Documents\nsfw",
}

EXTENSION_RULES = {
    ".exe": r"D:\Files\Downloads\exe",
}

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".mp4",
    ".exe"
}

# =========================
# Logging
# =========================

logging.basicConfig(
    filename="organizer.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


def wait_until_ready(filepath, timeout=10):
    """
    Tunggu sampai file tidak sedang digunakan
    oleh browser / explorer.
    """
    start = time.time()

    while time.time() - start < timeout:
        try:
            with open(filepath, "rb"):
                return True
        except (PermissionError, OSError):
            time.sleep(0.5)

    return False


def get_unique_destination(dst):
    """
    Hindari overwrite file.
    """

    if not os.path.exists(dst):
        return dst

    folder = os.path.dirname(dst)

    filename = os.path.basename(dst)
    name, ext = os.path.splitext(filename)

    counter = 1

    while True:
        new_name = f"{name}_{counter}{ext}"
        new_dst = os.path.join(folder, new_name)

        if not os.path.exists(new_dst):
            return new_dst

        counter += 1


def organize_file(filepath):

    if not os.path.isfile(filepath):
        return

    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return

    if not wait_until_ready(filepath):
        logging.warning(f"File locked: {filepath}")
        return

    filename = os.path.basename(filepath)

    if ext in EXTENSION_RULES:
        destination = EXTENSION_RULES[ext]
        try:
            os.makedirs(destination, exist_ok=True)
            dst = os.path.join(destination, filename)
            dst = get_unique_destination(dst)
            shutil.move(filepath, dst)
            logging.info(f"Moved | {filename} -> {destination}")
        except Exception:
            logging.exception(f"Failed moving: {filename}")
        return

    lower_name = filename.lower()

    for keyword, destination in RULES.items():

        if keyword.lower() in lower_name:

            try:
                os.makedirs(destination, exist_ok=True)

                dst = os.path.join(destination, filename)
                dst = get_unique_destination(dst)

                shutil.move(filepath, dst)

                logging.info(
                    f"Moved | {filename} -> {destination}"
                )

            except Exception:
                logging.exception(
                    f"Failed moving: {filename}"
                )

            return

    logging.info(
        f"No matching rule: {filename}"
    )


class FILEHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        logging.info(
            f"Created: {event.src_path}"
        )

        time.sleep(1)

        organize_file(event.src_path)

    def on_moved(self, event):

        if event.is_directory:
            return

        logging.info(
            f"Renamed/Moved: {event.dest_path}"
        )

        time.sleep(1)

        organize_file(event.dest_path)


if __name__ == "__main__":

    if not os.path.exists(SOURCE):
        logging.error(
            f"Source folder not found: {SOURCE}"
        )
        raise FileNotFoundError(SOURCE)

    logging.info("========== START ==========")
    logging.info(f"Watching: {SOURCE}")

    # Scan file lama saat startup
    for file in os.listdir(SOURCE):
        organize_file(
            os.path.join(SOURCE, file)
        )

    observer = Observer()

    observer.schedule(
        FILEHandler(),
        SOURCE,
        recursive=False
    )

    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()