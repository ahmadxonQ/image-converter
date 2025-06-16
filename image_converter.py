import os
import sys
import io
import shutil
from pathlib import Path



from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()

import tkinter as tk
from tkinter import filedialog, messagebox

import subprocess


MAX_KB = 800
MAX_WIDTH = 1280
OUTPUT_DIR = "output"
SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".heic"]


def compress_jpeg(img: Image.Image, output_path: Path):
    """Resize once and save as JPEG under MAX_KB."""
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

    buffer = io.BytesIO()
    img = img.convert("RGB")  # JPEG doesn’t support alpha
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    size_kb = len(buffer.getvalue()) / 1024

    if size_kb <= MAX_KB:
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
        return True
    else:
        print(f"⚠️ {output_path.name}: final size {int(size_kb)}KB exceeds {MAX_KB}KB")
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())  # Save anyway
        return False


def process_image(image_path: Path):
    try:
        img = Image.open(image_path)
        output_name = image_path.stem + ".jpg"
        output_path = Path(OUTPUT_DIR) / output_name
        success = compress_jpeg(img, output_path)
        if success:
            print(f"✅ {image_path.name} → {output_name}")
        else:
            print(f"❌ {image_path.name} could not be compressed under {MAX_KB}KB")
    except Exception as e:
        print(f"⚠️ Failed to process {image_path.name}: {e}")


def process_folder(folder: Path):
    count = 0
    for file in folder.rglob("*.*"):
        if file.suffix.lower() in SUPPORTED_EXTS:
            process_image(file)
            count += 1
    if count == 0:
        print("⚠️ No supported image files found in the folder.")
    return count


def process_input(path: Path) -> int:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    if path.is_file():
        process_image(path)
        return 1
    elif path.is_dir():
        return process_folder(path)
    else:
        print("❌ Invalid input path")
        return 0


# -------------- GUI --------------
def run_gui():
    def choose_file():
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff *.heic")]
        )
        if file_path:
            count = process_input(Path(file_path))
            if count:
                messagebox.showinfo("Done", f"Image processed and saved to '{OUTPUT_DIR}'")
            else:
                messagebox.showwarning("Failed", "Failed to process the selected image.")

    def choose_folder():
        folder_path = filedialog.askdirectory(title="Select a Folder with Images")
        if folder_path:
            folder = Path(folder_path)
            valid_images = [
                f for f in folder.rglob("*.*")
                if f.suffix.lower() in SUPPORTED_EXTS
            ]
            if not valid_images:
                messagebox.showwarning("No Images", "No supported images found in that folder.")
                return

            count = process_input(folder)
            if count:
                messagebox.showinfo("Done", f"Processed {count} image(s) to '{OUTPUT_DIR}'")
            else:
                messagebox.showwarning("Failed", "No images were processed.")

    # open folder
    def open_output_folder():
        output_path = os.path.abspath(OUTPUT_DIR)
        if not os.path.exists(output_path):
            messagebox.showwarning("Not Found", "Output folder does not exist yet.")
            return
        subprocess.run(["open", output_path])

   

    root = tk.Tk()
    root.title("Image to JPEG Converter")
    root.geometry("320x160")

    tk.Label(root, text="Select image or folder to convert to compressed JPEG").pack(pady=10)
    tk.Button(root, text="Choose Image File", command=choose_file, width=25).pack(pady=5)
    tk.Button(root, text="Choose Folder", command=choose_folder, width=25).pack(pady=5)

    tk.Button(root, text="Open Output Folder", command=open_output_folder, width=25).pack(pady=5)
    tk.Label(root, text="Output saved to './output'").pack(pady=10)
    

    root.mainloop()


if __name__ == "__main__":
    run_gui()
