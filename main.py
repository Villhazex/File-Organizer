import os
import time
import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SOURCE = r"D:\Files\Downloads"

RULES = {
    "pdsk": r"D:\Kuliah\PDSK",
    "so": r"D:\Kuliah\SOperasi",
}


def organize_pdf(filepath):
    if not os.path.isfile(filepath):
        return

    if not filepath.lower().endswith(".pdf"):
        return

    filename = os.path.basename(filepath)
    lower_name = filename.lower()

    for keyword, destination in RULES.items():
        if keyword in lower_name:

            os.makedirs(destination, exist_ok=True)

            dst = os.path.join(destination, filename)

            # Hindari overwrite
            if os.path.exists(dst):
                name, ext = os.path.splitext(filename)
                counter = 1

                while True:
                    new_name = f"{name}_{counter}{ext}"
                    dst = os.path.join(destination, new_name)

                    if not os.path.exists(dst):
                        break

                    counter += 1

            try:
                shutil.move(filepath, dst)

                print(f"\n✓ Moved")
                print(f"  File : {filename}")
                print(f"  To   : {destination}")

            except Exception as e:
                print(f"✗ Error moving {filename}: {e}")

            return


class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        # Tunggu download selesai ditulis
        time.sleep(1)

        organize_pdf(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return

        time.sleep(1)
        # Rename file juga masuk ke sini
        organize_pdf(event.dest_path)


if __name__ == "__main__":

    print(f"Watching: {SOURCE}")

    observer = Observer()
    observer.schedule(
        PDFHandler(),
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