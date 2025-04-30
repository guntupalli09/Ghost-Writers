import os
import requests
from pathlib import Path

def download_fonts():
    """Download Noto Sans fonts for PDF generation."""
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    # Noto Sans fonts
    font_urls = {
        "NotoSans-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
        "NotoSans-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
    }
    
    for filename, url in font_urls.items():
        font_path = fonts_dir / filename
        if not font_path.exists():
            print(f"Downloading {filename}...")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(font_path, "wb") as f:
                        f.write(response.content)
                    print(f"Successfully downloaded {filename}")
                else:
                    print(f"Failed to download {filename}: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading {filename}: {str(e)}")

if __name__ == "__main__":
    download_fonts() 