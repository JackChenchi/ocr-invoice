
import requests
import time
import sys
import os

API_URL = 'http://127.0.0.1:8000'
IMAGE_PATH = 'test_image.png'

def test_ocr_flow():
    print('Starting OCR integration test...', flush=True)

    if not os.path.exists(IMAGE_PATH):
        print(f'Error: Test image {IMAGE_PATH} not found', flush=True)
        sys.exit(1)

    # 1. Upload Image
    print(f'Uploading {IMAGE_PATH}...', flush=True)
    try:
        with open(IMAGE_PATH, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f'{API_URL}/ocr/upload', files=files)
        
        if response.status_code != 200:
            print(f'Upload failed: {response.text}', flush=True)
            sys.exit(1)
            
        data = response.json()
        task_id = data['id']
        print(f'Upload successful! Task ID: {task_id}, Status: {data["status"]}', flush=True)
    except Exception as e:
        print(f'Error during upload: {e}', flush=True)
        sys.exit(1)

if __name__ == '__main__':
    test_ocr_flow()
