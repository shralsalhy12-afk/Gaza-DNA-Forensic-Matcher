from modules.dna_matcher import calculate_str_match
from modules.encryption import anonymize_id
from modules.file_parser import load_dna_profile_from_file

def main():
    print("=" * 60)
    print("   Gaza DNA Forensic Matcher & Automated File Reader   ")
    print("=" * 60)

    # 1. إدخال وتشفير الهويات
    unidentified_id = input("\n[?] أدخل المعرف الميداني للرفات: ").strip()
    relative_id = input("[?] أدخل رقم هوية القريب المرجعي: ").strip()

    encrypted_unidentified = anonymize_id(unidentified_id)
    encrypted_relative = anonymize_id(relative_id)

    print(f"\n[*] الهويات المشفرة:")
    print(f"  - الرفات: {encrypted_unidentified}")
    print(f"  - القريب: {encrypted_relative}")

    # 2. قراءة ملفات البصمة الوراثية الصادرة من جهاز الفحص
    sample_file = input("\n[?] أدخل مسار ملف بصمة الرفات (مثال: sample.json): ").strip()
    reference_file = input("[?] أدخل مسار ملف بصمة القريب (مثال: reference.json): ").strip()

    sample_str = load_dna_profile_from_file(sample_file)
    reference_str = load_dna_profile_from_file(reference_file)

    if sample_str and reference_str:
        print("\n[+] تم استخراج البيانات الجينية من الملفات بنجاح!")
        result = calculate_str_match(sample_str, reference_str)

        print("\n" + "=" * 40)
        print("       التقرير الجنائي التلقائي للمطابقة       ")
        print("=" * 40)
        print(f"  - عدد المواقع الجينية الملتئمة: {result['matching_loci']} / {result['total_loci']}")
        print(f"  - نسبة التطابق الجيني: {result['match_percentage']}%")
        print(f"  - النتيجة الجنائية: {result['status']}")
    else:
        print("\n[-] تعذر إكمال المطابقة لعدم اكتمال بيانات الملفات.")

if __name__ == "__main__":
    main()
