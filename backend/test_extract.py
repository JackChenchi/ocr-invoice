import sys
sys.path.insert(0, '.')

from app.services.invoice_extractor import InvoiceExtractor

text = '''y — iS = AwashBank | anstTemsuccess[u Transaction Date 2026-03-08 16:48:33 Transaction Type Send To Bank Amount 320,000 ETB Charge 0.00 ETB VAT 0.00 ETB Sender Account 01425******700/BANK Sender Name ». yarmus Shemsu Ahmed Ky : \ Receiver Account a \ 25kxxxxx3300 < ? vu Recei N DUL AMIFTA TOFIK eceiver Name 动 U 人 / Reason Awash 1 Transaction ID 260308164857231 shank Voutonusing AwashBirE Prd A AAA AAA AAA AAA AAA AAA AAA'''

print("Testing extract_bank_receipt:")
info = InvoiceExtractor.extract_bank_receipt(text)
print(f"transaction_reference: {info.transaction_reference}")
print(f"amount: {info.amount}")
print(f"currency: {info.currency}")
print(f"transaction_date: {info.transaction_date}")
print(f"confidence: {info.confidence}")
