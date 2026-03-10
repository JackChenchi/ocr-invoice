import sqlite3
import sys
sys.path.insert(0, r'H:\Work\Trae\02_project_vote\backend')
from app.services.invoice_extractor import InvoiceExtractor

conn = sqlite3.connect(r'H:\Work\Trae\02_project_vote\backend\ocr.db')
cursor = conn.cursor()

cursor.execute("SELECT id, file_name, ocr_text FROM ocr_results ORDER BY id")
rows = cursor.fetchall()

print("=" * 80)
print("测试金额和交易编码识别")
print("=" * 80)

for row in rows:
    id_, file_name, ocr_text = row
    print(f"\n{'='*60}")
    print(f"ID: {id_}, 文件: {file_name}")
    print(f"{'='*60}")
    
    if not ocr_text:
        print("  [警告] 无OCR文本")
        continue
    
    info = InvoiceExtractor.extract_bank_receipt(ocr_text)
    
    print(f"  交易编码: {info.transaction_reference or '[缺失]'}")
    print(f"  金额: {info.amount or '[缺失]'}")
    print(f"  货币: {info.currency}")
    
    if not info.transaction_reference or not info.amount:
        print("\n  [调试] OCR文本片段:")
        lines = ocr_text.split('\n')
        for i, line in enumerate(lines[:30]):
            if line.strip():
                print(f"    {i}: {line[:100]}")

conn.close()
print("\n" + "=" * 80)
print("测试完成")
