import re

text = '''y — iS = AwashBank | anstTemsuccess[u Transaction Date 2026-03-08 16:48:33 Transaction Type Send To Bank Amount 320,000 ETB Charge 0.00 ETB VAT 0.00 ETB Sender Account 01425******700/BANK Sender Name ». yarmus Shemsu Ahmed Ky : \ Receiver Account a \ 25kxxxxx3300 < ? vu Recei N DUL AMIFTA TOFIK eceiver Name 动 U 人 / Reason Awash 1 Transaction ID 260308164857231 shank Voutonusing AwashBirE Prd A AAA AAA AAA AAA AAA AAA AAA'''

def parse_amount(amount_str):
    if not amount_str:
        return None
    try:
        cleaned = amount_str.replace(",", "").replace(" ", "").replace("￥", "").replace("¥", "")
        cleaned = re.sub(r"[A-Z]{3}", "", cleaned)
        return float(cleaned)
    except ValueError:
        return None

def _parse_bank_table(text):
    result = {}
    
    amount_patterns = [
        r'Amount[:\s]+([\d,]+\.?\d*)\s*([A-Z]{3})',
        r'Amount[:\s]*([A-Z]{3})\s*([\d,]+\.?\d*)',
        r'([A-Z]{3})\s+([\d,]+\.?\d*)',
        r'([\d,]+\.\d{2})\s*([A-Z]{3})',
        r'([A-Z]{3})\s*([\d,]+\.\d{2})',
    ]
    for amt_pattern in amount_patterns:
        amt_match = re.search(amt_pattern, text, re.IGNORECASE)
        if amt_match:
            groups = amt_match.groups()
            if len(groups) == 2:
                if groups[0] and groups[0].replace(',', '').replace('.', '').isdigit():
                    result["amount"] = groups[0].replace(',', '')
                    result["currency"] = groups[1] if groups[1].isalpha() else result.get("currency", "ETB")
                elif groups[1] and groups[1].replace(',', '').replace('.', '').isdigit():
                    result["currency"] = groups[0] if groups[0].isalpha() else result.get("currency", "ETB")
                    result["amount"] = groups[1].replace(',', '')
            break
    
    return result

table_data = _parse_bank_table(text)
print(f"table_data: {table_data}")

if table_data.get("amount"):
    print(f"\ntable_data['amount'] = '{table_data['amount']}'")
    print(f"table_data.get('currency') = '{table_data.get('currency')}'")
    
    amount_match = re.search(r'([A-Z]{3})\s*([\d,]+\.?\d*)', table_data["amount"])
    print(f"\namount_match on '{table_data['amount']}': {amount_match}")
    
    if amount_match:
        print(f"Match groups: {amount_match.groups()}")
        currency = amount_match.group(1)
        amount = parse_amount(amount_match.group(2))
    else:
        print("No match, using parse_amount directly")
        amount = parse_amount(table_data["amount"])
        currency = table_data.get("currency", "ETB")
    
    print(f"\nFinal: amount={amount}, currency={currency}")
