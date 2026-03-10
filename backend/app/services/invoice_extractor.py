import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class InvoiceInfo:
    invoice_code: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    invoice_type: Optional[str] = None
    
    buyer_name: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_bank: Optional[str] = None
    buyer_account: Optional[str] = None
    
    seller_name: Optional[str] = None
    seller_tax_id: Optional[str] = None
    seller_address: Optional[str] = None
    seller_phone: Optional[str] = None
    seller_bank: Optional[str] = None
    seller_account: Optional[str] = None
    
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    amount_without_tax: Optional[float] = None
    amount_in_words: Optional[str] = None
    
    currency: str = "CNY"
    check_code: Optional[str] = None
    remarks: Optional[str] = None
    
    raw_text: Optional[str] = None
    confidence: float = 0.0
    extraction_errors: List[str] = field(default_factory=list)

@dataclass
class BankReceiptInfo:
    bank_name: Optional[str] = None
    transaction_reference: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_time: Optional[str] = None
    transaction_type: Optional[str] = None
    
    source_account: Optional[str] = None
    source_account_name: Optional[str] = None
    source_bank: Optional[str] = None
    
    receiver_account: Optional[str] = None
    receiver_account_name: Optional[str] = None
    receiver_bank: Optional[str] = None
    
    amount: Optional[float] = None
    currency: str = "ETB"
    
    status: Optional[str] = None
    remarks: Optional[str] = None
    
    raw_text: Optional[str] = None
    confidence: float = 0.0
    extraction_errors: List[str] = field(default_factory=list)

class InvoiceExtractor:
    PATTERNS = {
        "invoice_code": [
            r"发票代码[:：]?\s*([A-Za-z0-9]{10,12})",
            r"代码[:：]?\s*([A-Za-z0-9]{10,12})",
            r"发票代码\s*([A-Za-z0-9]{10,12})",
        ],
        "invoice_number": [
            r"发票号码[:：]?\s*(\d{8,})",
            r"号码[:：]?\s*(\d{8,})",
            r"发票号码\s*(\d{8,})",
            r"No\.?\s*(\d{8,})",
        ],
        "invoice_date": [
            r"(?:开票日期|日期|开票时间)[:：]?\s*(\d{4}[-年/]\d{1,2}[-月/]\d{1,2}日?)",
            r"(\d{4}年\d{1,2}月\d{1,2}日)",
            r"(\d{4}[-/]\d{2}[-/]\d{2})",
        ],
        "buyer_name": [
            r"(?:购买方|购方|购货单位|买方)[名称名][:：]?\s*([^\n\r]{2,50}?)(?=\s*(?:纳税人|税号|识别号|地址|$))",
            r"名\s*称[:：]?\s*([^\n\r]{2,50}?)(?=\s*(?:纳税人|税号|识别号))",
            r"购买方[:：]?\s*([^\n\r]{2,30})",
        ],
        "buyer_tax_id": [
            r"(?:购买方|购方)[^)]*?(?:纳税人识别号|税号|识别号)[:：]?\s*([A-Za-z0-9]{15,20})",
            r"纳税人识别号[:：]?\s*([A-Za-z0-9]{15,20})",
            r"识别号[:：]?\s*([A-Za-z0-9]{15,20})",
        ],
        "seller_name": [
            r"(?:销售方|销方|销货单位|卖方)[名称名][:：]?\s*([^\n\r]{2,50}?)(?=\s*(?:纳税人|税号|识别号|地址|$))",
            r"销售方[:：]?\s*([^\n\r]{2,30})",
        ],
        "seller_tax_id": [
            r"(?:销售方|销方)[^)]*?(?:纳税人识别号|税号|识别号)[:：]?\s*([A-Za-z0-9]{15,20})",
        ],
        "total_amount": [
            r"(?:价税合计|合计金额|总金额|总计)[:：]?\s*[￥¥]?\s*([\d,]+\.?\d*)",
            r"[￥¥]\s*([\d,]+\.?\d*)\s*(?:元|$)",
            r"小写[:：]?\s*[￥¥]?\s*([\d,]+\.?\d*)",
        ],
        "tax_amount": [
            r"(?:税额|税金)[:：]?\s*[￥¥]?\s*([\d,]+\.?\d*)",
            r"税\s*额[:：]?\s*[￥¥]?\s*([\d,]+\.?\d*)",
        ],
        "amount_without_tax": [
            r"(?:金额|不含税金额|合计)[:：]?\s*[￥¥]?\s*([\d,]+\.?\d*)",
        ],
        "amount_in_words": [
            r"(?:大写|合计大写)[:：]?\s*([壹贰叁肆伍陆柒捌玖拾佰仟万亿零整圆角分]+)",
            r"大写[:：]?\s*([^\n\r]{5,50}?)(?=\s*(?:小写|￥|¥|$))",
        ],
        "check_code": [
            r"(?:校验码|验证码|校验码后六位)[:：]?\s*(\d{6,20})",
            r"校验码\s*(\d{6,20})",
        ],
        "address_phone": [
            r"(?:地址|地址电话)[:：]?\s*([^\n\r]{5,100}?)(?=\s*(?:开户|银行|账号|$))",
        ],
        "bank_account": [
            r"(?:开户行|开户银行)[:：]?\s*([^\n\r]{2,30}?)(?:\s*账号|\s*$)",
            r"(?:账号|银行账号)[:：]?\s*([\d\-]{8,30})",
        ],
    }

    BANK_PATTERNS = {
        "bank_name": [
            r"(Bank\s*(?:of\s*)?[A-Za-z]+)",
            r"([A-Za-z]+\s*Bank)",
            r"银行名称[:：]?\s*([^\n\r]+)",
        ],
        "transaction_reference": [
            r"TraRef([A-Za-z0-9]+)",
            r"Transaction\s*Reference[:\s]*([A-Za-z0-9\-_]+)",
            r"Transaction\s*ID[:\s]*([A-Za-z0-9\-_]+)",
            r"Reference\s*(?:No|Number)?[:\s]*([A-Za-z0-9\-_]{5,})",
            r"Ref\s*(?:No|Number)?[:\s]*([A-Za-z0-9\-_]+)",
            r"(FT\d+[A-Za-z]+\d+)",
            r"([A-Z]{2,4}\d{8,15})",
            r"([A-Z]{2,4}[\-_]\d{8,15})",
            r"Transaction[:\s]*([A-Za-z0-9\-_]{8,20})",
            r"ID[:\s]*([A-Za-z0-9\-_]{8,20})",
        ],
        "transaction_date": [
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{4}[-/]\d{2}[-/]\d{2})",
            r"Transaction\s*(?:Time|Date)[:\s]*(\d{2}/\d{2}/\d{4})",
        ],
        "transaction_time": [
            r"(\d{2}:\d{2}:\d{2})",
            r"Transaction\s*Time[:\s]*\d{2}/\d{2}/\d{4},?\s*(\d{2}:\d{2}:\d{2})",
        ],
        "transaction_type": [
            r"Transaction\s*Type[:\s]*([A-Za-z\s]+?)(?=\n|$)",
            r"(Within\s*[A-Z]+)",
            r"(Transfer|Payment|Credit|Debit)",
        ],
        "source_account": [
            r"Source\s*Account[:\s]*([\d\*]+)",
            r"(?:From|Sender)\s*Account[:\s]*([\d\*]+)",
            r"付款账号[:：]?\s*([\d\*]+)",
        ],
        "source_account_name": [
            r"Source\s*Account\s*Name[:\s]*([^\n\r]+)",
            r"Sender\s*Name[:\s]*([^\n\r]+)",
            r"付款人[:：]?\s*([^\n\r]+)",
        ],
        "receiver_account": [
            r"Receiver\s*Account[:\s]*([\d\*]+)",
            r"(?:To|Beneficiary)\s*Account[:\s]*([\d\*]+)",
            r"收款账号[:：]?\s*([\d\*]+)",
        ],
        "receiver_account_name": [
            r"Receiver\s*Name[:\s]*([^\n\r]+)",
            r"Beneficiary\s*Name[:\s]*([^\n\r]+)",
            r"收款人[:：]?\s*([^\n\r]+)",
        ],
        "amount": [
            r"Amount[:\s]*([A-Z]{3})\s*([\d,]+\.?\d*)",
            r"Amount[:\s]*([\d,]+\.?\d*)",
            r"([\d,]+\.\d{2})\s*(?:ETB|USD|EUR|CNY)",
        ],
        "currency": [
            r"Amount[:\s]*([A-Z]{3})\s*[\d,]+",
            r"(ETB|USD|EUR|CNY|GBP|JPY)",
        ],
        "status": [
            r"Status[:\s]*([A-Za-z]+)",
            r"(Completed|Pending|Failed|Success)",
        ],
    }

    CHINESE_NUM_MAP = {
        "零": 0, "壹": 1, "贰": 2, "叁": 3, "肆": 4,
        "伍": 5, "陆": 6, "柒": 7, "捌": 8, "玖": 9,
        "拾": 10, "佰": 100, "仟": 1000, "万": 10000,
        "亿": 100000000, "圆": 1, "元": 1, "角": 0.1, "分": 0.01,
        "整": 0, "正": 0,
    }

    @staticmethod
    def extract_field(text: str, field_name: str, patterns_dict: Dict = None) -> Optional[str]:
        patterns = patterns_dict.get(field_name, []) if patterns_dict else InvoiceExtractor.PATTERNS.get(field_name, [])
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                groups = match.groups()
                if len(groups) > 1:
                    return " ".join(g.strip() for g in groups if g)
                return match.group(1).strip()
        return None

    @staticmethod
    def parse_amount(amount_str: str) -> Optional[float]:
        if not amount_str:
            return None
        try:
            cleaned = amount_str.replace(",", "").replace(" ", "").replace("￥", "").replace("¥", "")
            cleaned = re.sub(r"[A-Z]{3}", "", cleaned)
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        if not date_str:
            return None
        
        date_str = date_str.replace("年", "-").replace("月", "-").replace("日", "")
        date_str = re.sub(r"[/\-]+", "-", date_str)
        
        try:
            parts = date_str.split("-")
            if len(parts) == 3:
                year = parts[0]
                month = parts[1].zfill(2)
                day = parts[2].zfill(2)
                return f"{year}-{month}-{day}"
        except Exception:
            pass
        
        return date_str

    @staticmethod
    def extract_buyer_info(text: str) -> Dict[str, Optional[str]]:
        buyer_section = ""
        
        buyer_match = re.search(
            r"(?:购买方|购方|购货单位)[^\n]*\n?([\s\S]{0,300}?)(?=(?:销售方|销方|销货单位|备注|$))",
            text, re.IGNORECASE
        )
        if buyer_match:
            buyer_section = buyer_match.group(1)
        
        return {
            "name": InvoiceExtractor.extract_field(buyer_section or text, "buyer_name"),
            "tax_id": InvoiceExtractor.extract_field(buyer_section or text, "buyer_tax_id"),
        }

    @staticmethod
    def extract_seller_info(text: str) -> Dict[str, Optional[str]]:
        seller_section = ""
        
        seller_match = re.search(
            r"(?:销售方|销方|销货单位)[^\n]*\n?([\s\S]{0,300}?)(?=(?:备注|价税合计|合计|$))",
            text, re.IGNORECASE
        )
        if seller_match:
            seller_section = seller_match.group(1)
        
        return {
            "name": InvoiceExtractor.extract_field(seller_section or text, "seller_name"),
            "tax_id": InvoiceExtractor.extract_field(seller_section or text, "seller_tax_id"),
        }

    @staticmethod
    def extract(text: str) -> InvoiceInfo:
        info = InvoiceInfo()
        info.raw_text = text
        
        text_clean = re.sub(r"\s+", " ", text)
        
        info.invoice_code = InvoiceExtractor.extract_field(text_clean, "invoice_code")
        info.invoice_number = InvoiceExtractor.extract_field(text_clean, "invoice_number")
        
        date_str = InvoiceExtractor.extract_field(text_clean, "invoice_date")
        info.invoice_date = InvoiceExtractor.parse_date(date_str)
        
        buyer_info = InvoiceExtractor.extract_buyer_info(text_clean)
        info.buyer_name = buyer_info["name"]
        info.buyer_tax_id = buyer_info["tax_id"]
        
        seller_info = InvoiceExtractor.extract_seller_info(text_clean)
        info.seller_name = seller_info["name"]
        info.seller_tax_id = seller_info["tax_id"]
        
        total_str = InvoiceExtractor.extract_field(text_clean, "total_amount")
        info.total_amount = InvoiceExtractor.parse_amount(total_str)
        
        tax_str = InvoiceExtractor.extract_field(text_clean, "tax_amount")
        info.tax_amount = InvoiceExtractor.parse_amount(tax_str)
        
        amount_str = InvoiceExtractor.extract_field(text_clean, "amount_without_tax")
        info.amount_without_tax = InvoiceExtractor.parse_amount(amount_str)
        
        info.amount_in_words = InvoiceExtractor.extract_field(text_clean, "amount_in_words")
        info.check_code = InvoiceExtractor.extract_field(text_clean, "check_code")
        
        filled_fields = sum(1 for k, v in info.__dict__.items() 
                          if v is not None and k not in ["raw_text", "confidence", "extraction_errors"])
        info.confidence = min(1.0, filled_fields / 15.0)
        
        return info

    @staticmethod
    def extract_bank_receipt(text: str) -> BankReceiptInfo:
        info = BankReceiptInfo()
        info.raw_text = text
        
        table_data = InvoiceExtractor._parse_bank_table(text)
        if table_data:
            info.bank_name = table_data.get("bank_name") or InvoiceExtractor.extract_field(text, "bank_name", InvoiceExtractor.BANK_PATTERNS)
            info.source_account = table_data.get("source_account") or InvoiceExtractor.extract_field(text, "source_account", InvoiceExtractor.BANK_PATTERNS)
            info.source_account_name = table_data.get("source_account_name") or InvoiceExtractor.extract_field(text, "source_account_name", InvoiceExtractor.BANK_PATTERNS)
            info.receiver_account = table_data.get("receiver_account") or InvoiceExtractor.extract_field(text, "receiver_account", InvoiceExtractor.BANK_PATTERNS)
            info.receiver_account_name = table_data.get("receiver_account_name") or InvoiceExtractor.extract_field(text, "receiver_account_name", InvoiceExtractor.BANK_PATTERNS)
            info.transaction_reference = table_data.get("transaction_reference") or InvoiceExtractor.extract_field(text, "transaction_reference", InvoiceExtractor.BANK_PATTERNS)
            info.transaction_type = table_data.get("transaction_type") or InvoiceExtractor.extract_field(text, "transaction_type", InvoiceExtractor.BANK_PATTERNS)
            
            if table_data.get("transaction_time"):
                parts = table_data["transaction_time"].split(",")
                if len(parts) >= 1:
                    date_str = parts[0].strip()
                    info.transaction_date = InvoiceExtractor.parse_date(date_str)
                if len(parts) >= 2:
                    info.transaction_time = parts[1].strip()
            
            if table_data.get("amount"):
                amount_match = re.search(r'([A-Z]{3})\s*([\d,]+\.?\d*)', table_data["amount"])
                if amount_match:
                    info.currency = amount_match.group(1)
                    info.amount = InvoiceExtractor.parse_amount(amount_match.group(2))
                else:
                    info.amount = InvoiceExtractor.parse_amount(table_data["amount"])
        else:
            info.bank_name = InvoiceExtractor.extract_field(text, "bank_name", InvoiceExtractor.BANK_PATTERNS)
            info.transaction_reference = InvoiceExtractor.extract_field(text, "transaction_reference", InvoiceExtractor.BANK_PATTERNS)
            
            date_str = InvoiceExtractor.extract_field(text, "transaction_date", InvoiceExtractor.BANK_PATTERNS)
            info.transaction_date = InvoiceExtractor.parse_date(date_str)
            
            info.transaction_time = InvoiceExtractor.extract_field(text, "transaction_time", InvoiceExtractor.BANK_PATTERNS)
            info.transaction_type = InvoiceExtractor.extract_field(text, "transaction_type", InvoiceExtractor.BANK_PATTERNS)
            
            info.source_account = InvoiceExtractor.extract_field(text, "source_account", InvoiceExtractor.BANK_PATTERNS)
            info.source_account_name = InvoiceExtractor.extract_field(text, "source_account_name", InvoiceExtractor.BANK_PATTERNS)
            
            info.receiver_account = InvoiceExtractor.extract_field(text, "receiver_account", InvoiceExtractor.BANK_PATTERNS)
            info.receiver_account_name = InvoiceExtractor.extract_field(text, "receiver_account_name", InvoiceExtractor.BANK_PATTERNS)
            
            amount_str = InvoiceExtractor.extract_field(text, "amount", InvoiceExtractor.BANK_PATTERNS)
            info.amount = InvoiceExtractor.parse_amount(amount_str)
            
            currency = InvoiceExtractor.extract_field(text, "currency", InvoiceExtractor.BANK_PATTERNS)
            if currency:
                info.currency = currency.upper()
        
        info.status = InvoiceExtractor.extract_field(text, "status", InvoiceExtractor.BANK_PATTERNS)
        
        filled_fields = sum(1 for k, v in info.__dict__.items() 
                          if v is not None and k not in ["raw_text", "confidence", "extraction_errors", "currency"])
        info.confidence = min(1.0, filled_fields / 12.0)
        
        return info
    
    @staticmethod
    def _parse_bank_table(text: str) -> Dict[str, str]:
        result = {}
        
        ref_patterns = [
            r'TRANSACTION\s*REF\.?\s*[:\s]*([A-Z0-9]{10,})',
            r'Tran\s*Ref[:\s]+([A-Z]{2}\d{6,8}[A-Za-z0-9]{2,4})',
            r'TraRef([A-Za-z0-9]+)',
            r'Transfer\s*ID[:\s]+([A-Za-z0-9]+)',
            r'(FT\d{5,8}[A-Za-z0-9]{2,6})',
            r'(FT\d{8,})',
            r'Transaction\s*Reference\s+([A-Z0-9]{8,})',
            r'Transaction\s*ID[:\s]+([A-Za-z0-9\-_]{5,})',
            r'Trn\s*Ref[:\s]+([A-Za-z0-9\-_]{5,})',
            r'Reference\s+No\.?[:\s]*([A-Za-z0-9\-_]{5,})',
            r'Ref\s+No\.?[:\s]*([A-Za-z0-9\-_]{5,})',
            r'Ref\s+([A-Z]{2}\d{6,8}[A-Za-z0-9]{2,6})',
            r'([A-Z]{2,4}\d{10,20})',
            r'([A-Z]+-[A-Z]+-\d{4,})',
            r'Account[:\s]*\**(\d{4,})',
        ]
        for ref_pattern in ref_patterns:
            ref_match = re.search(ref_pattern, text, re.IGNORECASE)
            if ref_match:
                ref_value = ref_match.group(1).strip()
                if ref_value.upper() not in ['COMPLETED', 'PENDING', 'SUCCESS', 'FAILED', 'ERENCE', 'ERENCE']:
                    if len(ref_value) >= 5 and any(c.isdigit() for c in ref_value):
                        result["transaction_reference"] = ref_value
                        break
        
        def fix_amount(amount_str):
            amount_str = amount_str.replace(',', '')
            if '.' in amount_str:
                parts = amount_str.split('.')
                if len(parts) > 2:
                    last_part = parts[-1]
                    if len(last_part) == 2 and last_part.isdigit():
                        amount_str = ''.join(parts[:-1]) + '.' + last_part
                    else:
                        amount_str = ''.join(parts)
            return amount_str
        
        def is_valid_amount(amount_str):
            try:
                val = float(amount_str)
                return val > 0
            except:
                return False
        
        debit_patterns = [
            r'ETB\s*(\d+[\d.]+)\s+debited',
            r'ETB\s*([\d,]+\.?\d*)\s*debited',
            r'([\d,]+\.?\d*)\s*ETB\s*debited',
            r'debited[^A-Z]*?ETB\s*([\d,]+\.?\d*)',
            r'debited[^A-Z]*?([\d,]+\.?\d*)\s*ETB',
        ]
        for pattern in debit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_val = fix_amount(match.group(1))
                if is_valid_amount(amount_val):
                    result["amount"] = amount_val
                    result["currency"] = "ETB"
                    break
        
        if not result.get("amount"):
            etb_patterns = [
                r'ETB\s*([\d,]+\.\d{2})',
                r'ETB\s*([\d,]+)',
                r'([\d,]+\.\d{2})\s*ETB',
                r'([\d,]+)\s*ETB',
            ]
            for etb_pattern in etb_patterns:
                etb_match = re.search(etb_pattern, text, re.IGNORECASE)
                if etb_match:
                    amount_val = fix_amount(etb_match.group(1))
                    if is_valid_amount(amount_val):
                        result["amount"] = amount_val
                        result["currency"] = "ETB"
                        break
        
        if not result.get("amount"):
            amount_patterns = [
                r'Amount[:\s]+([A-Z]{3})\s+([\d,]+\.?\d*)',
                r'Amount[:\s]+([\d,]+\.?\d*)\s+([A-Z]{3})',
                r'Amount[:\s]+([\d,]+\.?\d*)([A-Z]{3})',
                r'([\d,]+\.\d{2})\s*ETB',
                r'Total\s*Amount[:\s]*([\d,]+\.?\d*)',
                r'Debit\s*Amt\.?[:\s]*([A-Z]{3})?\s*([\d,]+\.?\d*)',
                r'Credit\s*Amt\.?[:\s]*([A-Z]{3})?\s*([\d,]+\.?\d*)',
            ]
            for amt_pattern in amount_patterns:
                amt_match = re.search(amt_pattern, text, re.IGNORECASE)
                if amt_match:
                    groups = amt_match.groups()
                    if len(groups) == 2:
                        if groups[0] and groups[0].replace(',', '').replace('.', '').isdigit():
                            amount_val = groups[0].replace(',', '')
                            if len(amount_val) >= 3 and float(amount_val) > 0:
                                result["amount"] = amount_val
                                result["currency"] = groups[1] if groups[1] and groups[1].isalpha() else "ETB"
                                break
                        elif groups[1] and groups[1].replace(',', '').replace('.', '').isdigit():
                            amount_val = groups[1].replace(',', '')
                            if len(amount_val) >= 3 and float(amount_val) > 0:
                                result["currency"] = groups[0] if groups[0] and groups[0].isalpha() else "ETB"
                                result["amount"] = amount_val
                                break
                    elif len(groups) == 1 and groups[0]:
                        amount_val = groups[0].replace(',', '')
                        if len(amount_val) >= 3 and amount_val.replace('.', '').isdigit() and float(amount_val) > 0:
                            result["amount"] = amount_val
                            result["currency"] = "ETB"
                            break
        
        bank_patterns = [
            r'(Bank of Abyssinia)',
            r'(Commercial Bank of Ethiopia)',
            r'(Dashen Bank)',
            r'(Awash Bank)',
            r'(Zemen Bank)',
            r'(Bank of America)',
            r'(Chase Bank)',
            r'(Wells Fargo)',
            r'(HSBC)',
            r'(Citibank)',
            r'(Standard Chartered)',
            r'(Barclays)',
            r'(Deutsche Bank)',
            r'(UBS)',
            r'(ING)',
            r'(BNP Paribas)',
            r'(Santander)',
            r'(Rabobank)',
            r'(ABN AMRO)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Bank)',
        ]
        for bp in bank_patterns:
            bank_match = re.search(bp, text)
            if bank_match:
                result["bank_name"] = bank_match.group(1)
                break
        
        name_patterns = [
            r'(\d{1,4}\*+\d{3,4})\s+([A-Z][A-Za-z\u4e00-\u9fff\s/\-\.]+?)(?=\s+[A-Z]{3}\s+[\d,]|\s+\d{2}/\d{2}/\d{4})',
            r'From[:\s]*([A-Z][A-Za-z\u4e00-\u9fff\s/\-\.]+?)(?=\s+Account|\s+\d{1,4}\*)',
            r'To[:\s]*([A-Z][A-Za-z\u4e00-\u9fff\s/\-\.]+?)(?=\s+Account|\s+\d{1,4}\*)',
            r'Name[:\s]*([A-Z][A-Za-z\u4e00-\u9fff\s/\-\.]+?)(?=\s+[A-Z]{3}|\s+\d)',
            r'Sender[:\s]*([A-Z][A-Za-z\u4e00-\u9fff\s/\-\.]+?)(?=\s+[A-Z]{3}|\s+\d)',
            r'Receiver[:\s]*([A-Z][A-Za-z\u4e00-\u9fff\s/\-\.]+?)(?=\s+[A-Z]{3}|\s+\d)',
        ]
        names = []
        for np in name_patterns:
            name_matches = re.findall(np, text)
            for match in name_matches:
                if isinstance(match, tuple):
                    name = match[1].strip() if len(match) > 1 else match[0].strip()
                else:
                    name = match.strip()
                if name and len(name) > 2:
                    names.append(name)
        names = list(dict.fromkeys(names))
        if len(names) >= 1:
            result["source_account_name"] = names[0]
        if len(names) >= 2:
            result["receiver_account_name"] = names[1]
        
        return result

    @staticmethod
    def to_dict(info: Any) -> Dict[str, Any]:
        if isinstance(info, BankReceiptInfo):
            return {
                "bank_name": info.bank_name,
                "transaction_reference": info.transaction_reference,
                "transaction_date": info.transaction_date,
                "transaction_time": info.transaction_time,
                "transaction_type": info.transaction_type,
                "source_account": info.source_account,
                "source_account_name": info.source_account_name,
                "receiver_account": info.receiver_account,
                "receiver_account_name": info.receiver_account_name,
                "amount": info.amount,
                "currency": info.currency,
                "status": info.status,
                "confidence": info.confidence,
                "extraction_errors": info.extraction_errors,
            }
        else:
            return {
                "invoice_code": info.invoice_code,
                "invoice_number": info.invoice_number,
                "invoice_date": info.invoice_date,
                "invoice_type": info.invoice_type,
                "buyer_name": info.buyer_name,
                "buyer_tax_id": info.buyer_tax_id,
                "seller_name": info.seller_name,
                "seller_tax_id": info.seller_tax_id,
                "total_amount": info.total_amount,
                "tax_amount": info.tax_amount,
                "amount_without_tax": info.amount_without_tax,
                "amount_in_words": info.amount_in_words,
                "check_code": info.check_code,
                "confidence": info.confidence,
                "extraction_errors": info.extraction_errors,
            }

invoice_extractor = InvoiceExtractor()
