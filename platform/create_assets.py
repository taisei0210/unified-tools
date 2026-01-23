import shutil
import os
from pathlib import Path

def create_zip():
    source_dir = Path(r"c:\バイブコーディング\screenshot_shortcut")
    output_dir = Path(r"c:\バイブコーディング\platform\static\downloads")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_filename = output_dir / "screenshot_shortcut"
    
    print(f"Zipping {source_dir} to {output_filename}.zip...")
    
    # Create zip
    shutil.make_archive(str(output_filename), 'zip', source_dir)
    
    print("Done!")

if __name__ == "__main__":
    create_zip()
