# scripts/download_reads.py
import os
import requests

READS = {
    "left": "https://github.com/trinityrnaseq/trinityrnaseq/raw/master/sample_data/test_Trinity_Assembly/reads.left.fq.gz",
    "right": "https://github.com/trinityrnaseq/trinityrnaseq/raw/master/sample_data/test_Trinity_Assembly/reads.right.fq.gz"
}

DATA_DIR = "../data"

def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded {dest_path}")
    else:
        print(f"Failed to download {url}")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for name, url in READS.items():
        dest = os.path.join(DATA_DIR, f"reads.{name}.fq.gz")
        if not os.path.exists(dest):
            download_file(url, dest)
        else:
            print(f"{dest} already exists, skipping.")

if __name__ == "__main__":
    main()
