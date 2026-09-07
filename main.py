from modules.dna_matcher import calculate_str_match
from modules.encryption import anonymize_id
from modules.database import init_db, seed_sample_data, run_batch_matching

def main():
    # 1. تهيئة قاعدة البيانات المحلية وتعبئتها بسجلات حية
    init_db()
    seed_sample_data()

    print("=" * 65)
    print("   Gaza DNA Forensic Matcher & Automated Database Engine   ")
    print("   Humanitarian Disaster Victim Identification (DVI)       ")
    print("=" * 65)

    print("\nاختر نظام التشغيل المطلوب:")
    print("  1. إجراء مطابقة فردية مباشرة (Direct Single Match)")
    print("  2. تشغيل الفحص الشامل المتموج (Automated Batch Matching Engine)")

    choice = input("\n[?] أدخل اختيارك (1 أو 2): ").strip()

    if choice == '1':
        # التشغيل المباشر التقليدي لعينة واحدة
        unidentified_id = input("\n[?] أدخل المعرف الميداني للرفات (مثال: KY-2026-081): ").strip()
        relative_id = input("[?] أدخل رقم هوية القريب المرجعي (مثال: 401234567): ").strip()

        encrypted_unidentified = anonymize_id(unidentified_id)
        encrypted_relative = anonymize_id(relative_id)

        # بصمات جينية مباشرة داخل الكود
        sample_str = {"D3S1358": [15, 18], "vWA": [14, 17], "FGA": [20, 24], "D8S1179": [12, 13], "D21S11": [28, 30]}
        reference_str = {"D3S1358": [15, 16], "vWA": [14, 18], "FGA": [20, 22], "D8S1179": [12, 14], "D21S11": [29, 31]}

        print(f"\n[*] بيانات العينة المباشرة المشفرة:")
        print(f"  - الرفات: {encrypted_unidentified}")
        print(f"  - القريب: {encrypted_relative}")

        result = calculate_str_match(sample_str, reference_str)

        print("\n" + "=" * 40)
        print("       التقرير الجنائي للمطابقة الفردية       ")
        print("=" * 40)
        print(f"  - المواقع الجينية الملتئمة: {result['matching_loci']} / {result['total_loci']}")
        print(f"  - نسبة التطابق الجيني: {result['match_percentage']}%")
        print(f"  - النتيجة: {result['status']}")

    elif choice == '2':
        # تشغيل محرك المطابقة الجماعي من قاعدة البيانات
        print("\n[*] جاري تشغيل محرك الفحص الآلي لمسح جميع السجلات في قاعدة البيانات...")
        matches = run_batch_matching(threshold=70.0)

        print("\n" + "=" * 65)
        print(f"   نتائج المسح الآلي الشامل لقاعدة البيانات (تم العثور على {len(matches)} مطابقة)   ")
        print("=" * 65)

        if matches:
            for idx, match in enumerate(matches, 1):
                print(f"\n[{idx}] مطابقة مكتشفة:")
                print(f"  - رمز الرفات المشفر: {match['remains_code']}")
                print(f"  - رمز القريب المشفر: {match['relative_code']}")
                print(f"  - نسبة التطابق: {match['percentage']}%")
                print(f"  - التقييم الجنائي: {match['status']}")
        else:
            print("\n[-] لم يتم العثور على تطابقات تتجاوز النسبة المطلوبة.")
    else:
        print("\n[-] اختيار غير صحيح.")

if __name__ == "__main__":
    main()
