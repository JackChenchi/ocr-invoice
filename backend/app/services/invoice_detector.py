import re
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InvoiceType(str, Enum):
    VAT_SPECIAL = "增值税专用发票"
    VAT_ORDINARY = "增值税普通发票"
    VAT_ELECTRONIC = "增值税电子发票"
    VAT_ELECTRONIC_SPECIAL = "增值税电子专用发票"
    GENERAL_MACHINE = "通用机打发票"
    TOLL = "通行费发票"
    BANK_RECEIPT = "银行转账凭证"
    BANK_STATEMENT = "银行对账单"
    OTHER = "其他票据"
    NOT_INVOICE = "非票据"

INVOICE_KEYWORDS = {
    InvoiceType.VAT_SPECIAL: [
        "增值税专用发票", "专用发票", "抵扣联", "发票联",
        "购买方", "销售方", "税率", "税额", "价税合计"
    ],
    InvoiceType.VAT_ORDINARY: [
        "增值税普通发票", "普通发票", "购买方", "销售方",
        "价税合计", "收款人", "复核人"
    ],
    InvoiceType.VAT_ELECTRONIC: [
        "增值税电子发票", "电子发票", "购买方", "销售方"
    ],
    InvoiceType.VAT_ELECTRONIC_SPECIAL: [
        "增值税电子专用发票", "电子专用发票"
    ],
    InvoiceType.GENERAL_MACHINE: [
        "机打发票", "通用机打", "发票代码", "发票号码"
    ],
    InvoiceType.TOLL: [
        "通行费", "高速公路", "路桥费"
    ],
    InvoiceType.BANK_RECEIPT: [
        "bank", "transaction", "transfer", "receipt",
        "source account", "receiver account", "amount",
        "transaction reference", "transaction time",
        "sender", "beneficiary", "swift", "iban",
        "转账", "汇款", "收款人", "付款人", "汇款凭证",
        "transaction type", "credit", "debit"
    ],
    InvoiceType.BANK_STATEMENT: [
        "account statement", "bank statement",
        "balance", "opening balance", "closing balance",
        "对账单", "账户明细", "流水"
    ]
}

INVOICE_HEADER_PATTERNS = [
    r"全国统一发票监制章",
    r"发票监制章",
    r"国家税务总局",
    r"增值税.*发票",
    r"发票代码[:：]?\s*\d+",
    r"发票号码[:：]?\s*\d+",
    r"开票日期[:：]?\s*\d{4}",
]

BANK_RECEIPT_PATTERNS = [
    r"bank\s*(of|name)?",
    r"transaction\s*(reference|id|type|time)",
    r"(source|sender|from)\s*account",
    r"(receiver|beneficiary|to)\s*account",
    r"amount[:\s]*[\d,]+\.?\d*",
    r"transfer|remittance|payment",
    r"swift|iban|routing",
    r"account\s*(number|no\.?)",
    r"debit|credit",
    r"转账|汇款|付款|收款",
]

MAJOR_BANKS = [
    "bank of abyssinia", "commercial bank of ethiopia", "dashen bank",
    "awash bank", "zemen bank", "wegagen bank",
    "hsbc", "citibank", "jpmorgan", "bank of america",
    "wells fargo", "barclays", "deutsche bank", "ubs",
    "standard chartered", "hdfc", "icici", "sbi",
    "chase", "wells", "morgan", "中国银行", "工商银行",
    "建设银行", "农业银行", "交通银行", "招商银行",
]

class InvoiceDetector:
    @staticmethod
    def detect_invoice_type(text: str) -> InvoiceType:
        text_lower = text.lower()
        text_clean = text.replace(" ", "").replace("\n", "")
        
        bank_score = 0
        for pattern in BANK_RECEIPT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                bank_score += 1
        
        for bank in MAJOR_BANKS:
            if bank.lower() in text_lower:
                bank_score += 2
        
        if bank_score >= 3:
            if "statement" in text_lower:
                return InvoiceType.BANK_STATEMENT
            return InvoiceType.BANK_RECEIPT
        
        has_invoice_header = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in INVOICE_HEADER_PATTERNS
        )
        
        if not has_invoice_header:
            if not any(kw in text_clean for kw in ["发票", "金额", "税额", "价税"]):
                if bank_score >= 1:
                    return InvoiceType.BANK_RECEIPT
                return InvoiceType.NOT_INVOICE
        
        scores = {}
        for invoice_type, keywords in INVOICE_KEYWORDS.items():
            if invoice_type in [InvoiceType.BANK_RECEIPT, InvoiceType.BANK_STATEMENT]:
                continue
            score = sum(1 for kw in keywords if kw in text_clean or kw.lower() in text_lower)
            scores[invoice_type] = score
        
        max_score = max(scores.values()) if scores else 0
        if max_score == 0:
            if bank_score >= 1:
                return InvoiceType.BANK_RECEIPT
            return InvoiceType.OTHER if has_invoice_header else InvoiceType.NOT_INVOICE
        
        for invoice_type, score in scores.items():
            if score == max_score:
                return invoice_type
        
        return InvoiceType.OTHER

    @staticmethod
    def is_invoice(text: str, confidence_threshold: float = 0.2) -> Dict[str, Any]:
        invoice_type = InvoiceDetector.detect_invoice_type(text)
        
        is_valid = invoice_type != InvoiceType.NOT_INVOICE
        
        text_clean = text.replace(" ", "").replace("\n", "")
        text_lower = text.lower()
        
        keyword_count = 0
        for inv_type, keywords in INVOICE_KEYWORDS.items():
            for kw in keywords:
                if kw in text_clean or kw.lower() in text_lower:
                    keyword_count += 1
        
        bank_pattern_matches = sum(
            1 for pattern in BANK_RECEIPT_PATTERNS 
            if re.search(pattern, text_lower, re.IGNORECASE)
        )
        keyword_count += bank_pattern_matches
        
        confidence = min(1.0, keyword_count / 8.0)
        
        return {
            "is_invoice": is_valid,
            "invoice_type": invoice_type.value if isinstance(invoice_type, InvoiceType) else invoice_type,
            "confidence": confidence,
            "detected_keywords": keyword_count
        }

    @staticmethod
    def validate_invoice_structure(text: str) -> Dict[str, bool]:
        text_clean = text.replace(" ", "").replace("\n", "")
        text_lower = text.lower()
        
        is_bank_receipt = bool(re.search(r"bank|transaction|transfer", text_lower, re.IGNORECASE))
        
        if is_bank_receipt:
            structure = {
                "has_bank_name": bool(re.search(r"bank\s*(of|name)?", text_lower, re.IGNORECASE)),
                "has_transaction_id": bool(re.search(r"transaction\s*(reference|id|ref)", text_lower, re.IGNORECASE)),
                "has_date": bool(re.search(r"(date|time|日期|时间)[:：]?\s*\d{1,4}[-/]\d{1,2}[-/]\d{1,4}", text_lower, re.IGNORECASE)),
                "has_sender": bool(re.search(r"(source|sender|from|付款|汇款人)", text_lower, re.IGNORECASE)),
                "has_receiver": bool(re.search(r"(receiver|beneficiary|to|收款|受益人)", text_lower, re.IGNORECASE)),
                "has_amount": bool(re.search(r"amount[:\s]*[\d,]+\.?\d*", text_lower, re.IGNORECASE)),
                "has_account": bool(re.search(r"account\s*(number|no\.?)?", text_lower, re.IGNORECASE)),
            }
        else:
            structure = {
                "has_invoice_code": bool(re.search(r"发票代码[:：]?\s*[\dA-Za-z]{8,}", text_clean)),
                "has_invoice_number": bool(re.search(r"发票号码[:：]?\s*\d{6,}", text_clean)),
                "has_date": bool(re.search(r"(开票日期|日期|时间)[:：]?\s*\d{4}[-年/]\d{1,2}[-月/]\d{1,2}", text_clean)),
                "has_buyer": bool(re.search(r"(购买方|购方|购货单位|买方)", text_clean)),
                "has_seller": bool(re.search(r"(销售方|销方|销货单位|卖方)", text_clean)),
                "has_amount": bool(re.search(r"(金额|合计|总计|价税合计|大写)", text_clean)),
                "has_tax": bool(re.search(r"(税额|税率|税)", text_clean)),
            }
        
        structure["is_complete"] = sum(structure.values()) >= 4
        
        return structure

invoice_detector = InvoiceDetector()
