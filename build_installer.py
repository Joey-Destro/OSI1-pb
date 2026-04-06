import os
import subprocess
import shutil

def build():
    print("Building UsirevAI with PyInstaller...")

    # We use --onedir (default) instead of --onefile.
    # PyTorch and transformers are massive, and a single file executable
    # would take a very long time to extract every time the app is launched.

    command = [
        "pyinstaller",
        "--name", "UsirevAI",
        "--add-data", "static:static",
        "--noconfirm", # Overwrite output directory
        "--clean",
        "main.py"
    ]

    try:
        subprocess.run(command, check=True)
        print("PyInstaller build finished.")

        # Now create a zip file from the dist/UsirevAI directory
        print("Zipping the built application...")
        dist_dir = os.path.join("dist", "UsirevAI")
        shutil.make_archive("UsirevAI_LocalApp", "zip", dist_dir)
        print("Successfully created UsirevAI_LocalApp.zip")

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
