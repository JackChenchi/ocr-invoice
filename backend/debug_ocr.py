import sqlite3
import re

conn = sqlite3.connect(r'H:\Work\Trae\02_project_vote\backend\ocr.db')
cursor = conn.cursor()

cursor.execute("SELECT id, file_name, ocr_text FROM ocr_results WHERE id = 4")
row = cursor.fetchone()

if row:
    id_, file_name, ocr_text = row
    print(f"ID: {id_}, 文件: {file_name}")
    print("=" * 80)
    print("OCR文本:")
    print(ocr_text)
    print("=" * 80)
    
    print("\n测试交易编码识别:")
    ref_patterns = [
        r'Transaction\s*ID[:\s]*([A-Za-z0-9\-_]{5,})',
        r'Transfer\s*ID[:\s]*([A-Za-z0-9\-_]{5,})',
        r'Transaction\s*Reference[:\s]*([A-Za-z0-9\-_]{5,})',
        r'Transaction\s*Reference\s*([A-Z]{2,}\d+[A-Z]*\d*)',
        r'Reference[:\s]*([A-Za-z0-9\-_]{5,})',
        r'Ref[:\s]*([A-Za-z0-9\-_]{5,})',
        r'(FT\d{5}[A-Z]+\d{0,2})',
        r'(FT\d{8,})',
        r'([A-Z]{2,4}\d{10,20})',
        r'ID[:\s]*([A-Za-z0-9\-_]{8,})',
    ]
    
    for pattern in ref_patterns:
        matches = re.findall(pattern, ocr_text, re.IGNORECASE)
        if matches:
            print(f"  模式 '{pattern}': {matches}")
    
    print("\n测试金额识别:")
    amount_patterns = [
        r'ETB\s*([\d,]+\.?\d*)',
        r'Amount[:\s]+([\d,]+\.?\d*)\s*([A-Z]{3})',
        r'Amount[:\s]*([A-Z]{3})\s*([\d,]+\.?\d*)',
        r'([\d,]+\.\d{2})\s*ETB',
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, ocr_text, re.IGNORECASE)
        if matches:
            print(f"  模式 '{pattern}': {matches}")

conn.close()
