import sqlite3
import json

conn = sqlite3.connect('ocr.db')
cursor = conn.cursor()

cursor.execute('SELECT id, file_name, ocr_text, confidence FROM ocr_results ORDER BY id DESC LIMIT 5')
rows = cursor.fetchall()

print('=== 最近5条识别结果 ===')
for r in rows:
    print(f'\nID: {r[0]}')
    print(f'文件: {r[1]}')
    print(f'置信度: {r[3]}')
    text = r[2] if r[2] else '无'
    print(f'OCR文本前500字符:\n{text[:500]}...')
    print('-' * 50)

conn.close()
