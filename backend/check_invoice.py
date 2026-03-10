import sqlite3

conn = sqlite3.connect('ocr.db')
cursor = conn.cursor()

cursor.execute('SELECT id, file_name, transaction_reference, total_amount, currency, status, raw_ocr_text FROM invoice_results ORDER BY id DESC LIMIT 3')
rows = cursor.fetchall()

print('=== 最近3条记录 ===')
for r in rows:
    print(f'\nID: {r[0]}')
    print(f'文件: {r[1]}')
    print(f'交易参考: {r[2]}')
    print(f'金额: {r[3]} {r[4]}')
    print(f'状态: {r[5]}')
    text = r[6] if r[6] else '无'
    print(f'OCR文本前800字符:\n{text[:800]}...')
    print('-' * 60)

conn.close()
