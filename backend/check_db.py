import sqlite3

conn = sqlite3.connect('ocr.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', cursor.fetchall())

cursor.execute("SELECT id, file_name, status, error_msg, is_invoice, invoice_confidence FROM invoice_results ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()
print('\nRecent records:')
for r in rows:
    print(f'ID: {r[0]}, File: {r[1]}, Status: {r[2]}, Error: {r[3]}, IsInvoice: {r[4]}, Conf: {r[5]}')

conn.close()
