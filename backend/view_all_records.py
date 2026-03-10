import sqlite3

conn = sqlite3.connect(r'H:\Work\Trae\02_project_vote\backend\ocr.db')
cursor = conn.cursor()

cursor.execute("SELECT id, file_name, ocr_text FROM ocr_results ORDER BY id")
rows = cursor.fetchall()

print("=" * 80)
print("所有数据库记录")
print("=" * 80)

for row in rows:
    id_, file_name, ocr_text = row
    print(f"\n{'='*60}")
    print(f"ID: {id_}, 文件: {file_name}")
    print(f"{'='*60}")
    
    if not ocr_text:
        print("  [无OCR文本]")
    else:
        print(f"  OCR文本长度: {len(ocr_text)} 字符")
        print("\n  OCR文本内容:")
        print("-" * 50)
        print(ocr_text[:500] if len(ocr_text) > 500 else ocr_text)
        print("-" * 50)

conn.close()
