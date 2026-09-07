import json
import os

def load_dna_profile_from_file(file_path: str) -> dict:
    """
    يقوم هذا الموديول بفتح وقراءة ملف البيانات الناتجة من جهاز الفحص الجيني
    واستخراج مواقع الـ STR منها تلقائياً.
    """
    if not os.path.exists(file_path):
        print(f"[-] خطأ: الملف {file_path} غير موجود.")
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # استخراج ملف الـ STR الجيني من داخل تقرير الجهاز
            return data.get("str_profile", {})
    except Exception as e:
        print(f"[-] خطأ أثناء قراءة ملف البصمة الوراثية: {e}")
        return {}
