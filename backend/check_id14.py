import sqlite3

conn = sqlite3.connect('ocr.db')
cursor = conn.cursor()

cursor.execute('''
SELECT id, file_name, transaction_reference, total_amount, currency, status, 
       invoice_type, is_invoice, invoice_confidence, raw_ocr_text 
FROM invoice_results WHERE id = 14
''')
row = cursor.fetchone()

if row:
    print(f'ID: {row[0]}')
    print(f'文件: {row[1]}')
    print(f'交易参考: {row[2]}')
    print(f'金额: {row[3]} {row[4]}')
    print(f'状态: {row[5]}')
    print(f'发票类型: {row[6]}')
    print(f'是否发票: {row[7]}')
    print(f'发票置信度: {row[8]}')
    print(f'\nOCR文本:\n{row[9][:1500]}')

conn.close()
