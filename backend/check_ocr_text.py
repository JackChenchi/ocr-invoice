import sqlite3

conn = sqlite3.connect('ocr.db')
cursor = conn.cursor()

cursor.execute("SELECT id, file_name, raw_ocr_text, invoice_confidence FROM invoice_results ORDER BY id DESC LIMIT 2")
rows = cursor.fetchall()
for r in rows:
    print(f'=== ID: {r[0]}, File: {r[1]}, Confidence: {r[3]} ===')
    print('OCR Text:')
    print(r[2] if r[2] else '(empty)')
    print()

conn.close()
