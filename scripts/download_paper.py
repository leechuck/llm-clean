import argparse
import urllib.request
import os

def download_file(url, output_path):
    if os.path.exists(output_path):
        print(f"File already exists at {output_path}, skipping download.")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    print(f"Downloading {url} to {output_path}...")
    try:
        # Add a user agent to avoid 403s on some academic sites
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a file from a URL.")
    parser.add_argument("--url", required=True, help="The URL to download.")
    parser.add_argument("--output", required=True, help="The local output path.")
    
    args = parser.parse_args()
    download_file(args.url, args.output)
