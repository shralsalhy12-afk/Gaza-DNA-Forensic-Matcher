import hashlib

def anonymize_id(raw_id: str) -> str:
    """
    تشفير المعرفات الشخصية (رقم الهوية / الاسم) وتحويلها إلى كود أمني غير قابل للعكس
    لحماية خصوصية الضحايا وعائلاتهم طبقاً لمعايير الطب الشرعي الدولي.
    """
    if not raw_id:
        return ""
    
    # استخدام خوارزمية SHA-256 لتوليد معرف أمني فريد بطول 16 حرفاً
    hashed = hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
    return f"REF-{hashed[:16].upper()}"
