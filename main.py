from modules.dna_matcher import calculate_str_match
from modules.encryption import anonymize_id

def main():
    print("=" * 60)
    print("   Gaza DNA Forensic Matcher & Identification System   ")
    print("   Humanitarian Disaster Victim Identification (DVI)   ")
    print("=" * 60)

    # إدخال بيانات الرفات المجهولة
    unidentified_id = input("\n[?] أدخل المعرف الميداني للرفات (أو مكان العثور): ").strip()
    encrypted_unidentified = anonymize_id(unidentified_id)

    # إدخال بيانات القريب المرجعي
    relative_id = input("[?] أدخل رقم هوية القريب المرجعي (أب/أم/ابن): ").strip()
    encrypted_relative = anonymize_id(relative_id)

    print("\n[*] جاري تشفير البيانات وحمايتها بأعلى معايير الأمان الجنائي...")
    print(f"  - معرف الرفات المشفر: {encrypted_unidentified}")
    print(f"  - معرف القريب المشفر: {encrypted_relative}")

    # نموذج عينات STR الجينية (Standard CODIS Loci)
    # ملاحظة: الأرقام تمثل عدد تكرارات الأليل في المواقع الجينية
    sample_str = {
        "D3S1358": [15, 18],
        "vWA": [14, 17],
        "FGA": [20, 24],
        "D8S1179": [12, 13],
        "D21S11": [28, 30]
    }

    reference_str = {
        "D3S1358": [15, 16], # مطابقة أليل 15
        "vWA": [14, 18],     # مطابقة أليل 14
        "FGA": [20, 22],     # مطابقة أليل 20
        "D8S1179": [12, 14], # مطابقة أليل 12
        "D21S11": [29, 31]  # لا توجد مطابقة في هذا الموقع
    }

    print("\n[*] جاري تحليل البصمات الوراثية وتطابق المواقع الجينية (STR Loci)...")
    result = calculate_str_match(sample_str, reference_str)

    print("\n" + "=" * 40)
    print("       التقرير الجنائي المبدئي للمطابقة       ")
    print("=" * 40)
    print(f"  - عدد المواقع الجينية الملتئمة: {result['matching_loci']} / {result['total_loci']}")
    print(f"  - نسبة التطابق الجيني: {result['match_percentage']}%")
    print(f"  - النتيجة الجنائية: {result['status']}")

    if result['mismatches']:
        print(f"  - المواقع غير المتطابقة: {', '.join(result['mismatches'])}")

if __name__ == "__main__":
    main()
