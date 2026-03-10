import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from app.services.invoice_extractor import InvoiceInfo

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0

class InvoiceValidator:
    TAX_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{15,20}$")
    INVOICE_CODE_PATTERN = re.compile(r"^[A-Za-z0-9]{10,12}$")
    INVOICE_NUMBER_PATTERN = re.compile(r"^\d{8,}$")
    
    @staticmethod
    def validate_tax_id(tax_id: Optional[str]) -> bool:
        if not tax_id:
            return False
        return bool(InvoiceValidator.TAX_ID_PATTERN.match(tax_id.strip()))
    
    @staticmethod
    def validate_invoice_code(code: Optional[str]) -> bool:
        if not code:
            return False
        return bool(InvoiceValidator.INVOICE_CODE_PATTERN.match(code.strip()))
    
    @staticmethod
    def validate_invoice_number(number: Optional[str]) -> bool:
        if not number:
            return False
        return bool(InvoiceValidator.INVOICE_NUMBER_PATTERN.match(number.strip()))
    
    @staticmethod
    def validate_date(date_str: Optional[str]) -> bool:
        if not date_str:
            return False
        
        patterns = [
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{4}/\d{2}/\d{2}$",
            r"^\d{4}年\d{2}月\d{2}日$",
        ]
        
        for pattern in patterns:
            if re.match(pattern, date_str):
                try:
                    date_part = re.sub(r"[年月日/]", "-", date_str)
                    datetime.strptime(date_part, "%Y-%m-%d")
                    return True
                except ValueError:
                    return False
        return False
    
    @staticmethod
    def validate_amount(amount: Optional[float]) -> bool:
        if amount is None:
            return False
        return amount >= 0 and amount < 1e12
    
    @staticmethod
    def validate_amount_consistency(
        total: Optional[float], 
        tax: Optional[float], 
        without_tax: Optional[float]
    ) -> Dict[str, Any]:
        result = {"is_consistent": True, "errors": [], "warnings": []}
        
        if total is None:
            return result
        
        if tax is not None and without_tax is not None:
            expected_total = without_tax + tax
            if abs(expected_total - total) > 0.01:
                result["is_consistent"] = False
                result["errors"].append(
                    f"金额不一致: 不含税金额({without_tax}) + 税额({tax}) = {expected_total}, "
                    f"但价税合计为 {total}"
                )
        
        if tax is not None and total is not None:
            if tax > total:
                result["is_consistent"] = False
                result["errors"].append(f"税额({tax})大于价税合计({total})")
            
            if total > 0:
                tax_rate = tax / total
                common_rates = [0.03, 0.06, 0.09, 0.13, 0.16, 0.17]
                if not any(abs(tax_rate - rate) < 0.01 for rate in common_rates):
                    result["warnings"].append(f"税率({tax_rate:.2%})不在常见税率范围内")
        
        return result
    
    @staticmethod
    def validate(invoice_info: InvoiceInfo) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        
        if invoice_info.invoice_code:
            if InvoiceValidator.validate_invoice_code(invoice_info.invoice_code):
                result.field_scores["invoice_code"] = 1.0
            else:
                result.warnings.append(f"发票代码格式异常: {invoice_info.invoice_code}")
                result.field_scores["invoice_code"] = 0.5
        else:
            result.errors.append("缺少发票代码")
            result.field_scores["invoice_code"] = 0.0
        
        if invoice_info.invoice_number:
            if InvoiceValidator.validate_invoice_number(invoice_info.invoice_number):
                result.field_scores["invoice_number"] = 1.0
            else:
                result.warnings.append(f"发票号码格式异常: {invoice_info.invoice_number}")
                result.field_scores["invoice_number"] = 0.5
        else:
            result.errors.append("缺少发票号码")
            result.field_scores["invoice_number"] = 0.0
        
        if invoice_info.invoice_date:
            if InvoiceValidator.validate_date(invoice_info.invoice_date):
                result.field_scores["invoice_date"] = 1.0
            else:
                result.warnings.append(f"日期格式异常: {invoice_info.invoice_date}")
                result.field_scores["invoice_date"] = 0.5
        else:
            result.errors.append("缺少开票日期")
            result.field_scores["invoice_date"] = 0.0
        
        if invoice_info.buyer_name:
            result.field_scores["buyer_name"] = 1.0
        else:
            result.warnings.append("缺少购买方名称")
            result.field_scores["buyer_name"] = 0.0
        
        if invoice_info.buyer_tax_id:
            if InvoiceValidator.validate_tax_id(invoice_info.buyer_tax_id):
                result.field_scores["buyer_tax_id"] = 1.0
            else:
                result.warnings.append(f"购买方税号格式异常: {invoice_info.buyer_tax_id}")
                result.field_scores["buyer_tax_id"] = 0.5
        
        if invoice_info.seller_name:
            result.field_scores["seller_name"] = 1.0
        else:
            result.warnings.append("缺少销售方名称")
            result.field_scores["seller_name"] = 0.0
        
        if invoice_info.seller_tax_id:
            if InvoiceValidator.validate_tax_id(invoice_info.seller_tax_id):
                result.field_scores["seller_tax_id"] = 1.0
            else:
                result.warnings.append(f"销售方税号格式异常: {invoice_info.seller_tax_id}")
                result.field_scores["seller_tax_id"] = 0.5
        
        if invoice_info.total_amount is not None:
            if InvoiceValidator.validate_amount(invoice_info.total_amount):
                result.field_scores["total_amount"] = 1.0
            else:
                result.warnings.append(f"金额异常: {invoice_info.total_amount}")
                result.field_scores["total_amount"] = 0.5
        else:
            result.errors.append("缺少价税合计金额")
            result.field_scores["total_amount"] = 0.0
        
        consistency = InvoiceValidator.validate_amount_consistency(
            invoice_info.total_amount,
            invoice_info.tax_amount,
            invoice_info.amount_without_tax
        )
        if not consistency["is_consistent"]:
            result.errors.extend(consistency["errors"])
        result.warnings.extend(consistency["warnings"])
        
        if invoice_info.tax_amount is not None:
            result.field_scores["tax_amount"] = 1.0
        
        critical_fields = ["invoice_code", "invoice_number", "invoice_date", "total_amount"]
        critical_score = sum(result.field_scores.get(f, 0.0) for f in critical_fields) / len(critical_fields)
        
        all_fields = list(result.field_scores.keys())
        overall_score = sum(result.field_scores.values()) / max(len(all_fields), 1)
        
        result.overall_score = overall_score
        result.is_valid = critical_score >= 0.5 and len(result.errors) <= 2
        
        return result

invoice_validator = InvoiceValidator()
