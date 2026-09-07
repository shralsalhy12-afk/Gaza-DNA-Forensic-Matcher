#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gaza DNA Forensic Matcher & Sequencer Integration System
=========================================================
النظام المكتمل لإدارة ومطابقة البصمات الجينية والتكامل مع أجهزة الفحص الجنائي.
"""

import os
import json
import sqlite3
from modules.dna_matcher import calculate_str_match
from modules.encryption import anonymize_id
from modules.database import (
    init_db, 
    seed_sample_data, 
    run_batch_matching, 
    insert_sample_from_sequencer_file,
    DB_NAME
)


def interactive_dna_entry():
    """
    دالة الإدخال اليدوي التفاعلي لأرقام الـ STR موقعاً بموقع من قبل الطبيب الشرعي.
    """
    print("\n" + "=" * 50)
    print(" === شاشة إدخال بصمة جينية جديدة (Manual STR Entry) ===")
    print("=" * 50)
    
    sample_code = input("[?] أدخل رمز العينة/الرفات (مثال: REF-2026-99): ").strip()
    if not sample_code:
        print("[-] رمز العينة مطلوب!")
        return

    is_remains_input = input("[?] هل هذه العينة لرفات؟ (y/n, الافتراضي y): ").strip().lower()
    is_remains = False if is_remains_input == 'n' else True

    # قائمة المواقع الجنائية الوراثية القياسية
    standard_loci = ['D3S1358', 'vWA', 'FGA', 'TH01', 'TPOX', 'CSF1PO', 'D18S51', 'D21S11']
    
    str_profile = {}
    print("\n[*] أدخل قيم الأليلات لكل موقع جيني (افصل بين القيم بفاصلة مثل: 15, 18):")
    print("    (اضغط Enter لتجاوز الموقع إذا لم يتوفر فحص له)\n")

    for locus in standard_loci:
        val = input(f"  - الموقع {locus:8s}: ").strip()
        if val:
            try:
                # تحويل النص المدخل إلى قائمة من الأرقام
                alleles = [float(x.strip()) for x in val.split(',') if x.strip()]
                if alleles:
                    str_profile[locus] = alleles
            except ValueError:
                print(f"    [!] إدخال خاطئ للموقع {locus}، تم تجاوزه.")

    if not str_profile:
        print("[-] لم يتم إدخال أي موقع جيني صحيح!")
        return

    # حفظ العينة في قاعدة البيانات
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    enc_code = anonymize_id(sample_code)
    table = "remains" if is_remains else "relatives"
    col = "sample_code" if is_remains else "relative_code"
    
    try:
        cursor.execute(f"INSERT OR REPLACE INTO {table} ({col}, str_profile) VALUES (?, ?)",
                       (enc_code, json.dumps(str_profile)))
        conn.commit()
        print(f"\n[✓] تم حفظ البصمة الجينية بنجاح للعينة: {sample_code} (رمز مشفر: {enc_code})")
    except Exception as e:
        print(f"[-] خطأ أثناء حفظ العينة في قاعدة البيانات: {e}")
    finally:
        conn.close()


def direct_single_match_ui():
    """
    واجهة إجراء المطابقة الفردية المباشرة بين عينة رفات وعينة عائلة.
    """
    print("\n" + "=" * 50)
    print(" === إجراء مطابقة فردية مباشرة (Direct Single Match) ===")
    print("=" * 50)
    
    rem_id = input("[?] أدخل رمز الرفات (مثال: REF-2026-001): ").strip()
    rel_id = input("[?] أدخل رقم هوية/رمز العائلة (مثال: FAM-PAL-101): ").strip()
    
    if not rem_id or not rel_id:
        print("[-] يرجى إدخال كافة الرموز المطلوبة!")
        return

    enc_rem = anonymize_id(rem_id)
    enc_rel = anonymize_id(rel_id)

    # البحث عن العينات في قاعدة البيانات
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT str_profile FROM remains WHERE sample_code = ?", (enc_rem,))
    rem_row = cursor.fetchone()

    cursor.execute("SELECT str_profile FROM relatives WHERE relative_code = ?", (enc_rel,))
    rel_row = cursor.fetchone()

    conn.close()

    if rem_row and rel_row:
        rem_profile = json.loads(rem_row[0])
        rel_profile = json.loads(rel_row[0])
        score = calculate_str_match(rem_profile, rel_profile)
        
        print("\n" + "-" * 40)
        print(" [✓] نتيجة المطابقة الجنائية:")
        print(f"  - رمز الرفات المشفر:   {enc_rem}")
        print(f"  - رمز العائلة المشفر:  {enc_rel}")
        print(f"  - نسبة التوافق الوراثي المتوقعة: {round(score, 2)}%")
        print("-" * 40)
    else:
        print("\n[!] لم يتم العثور على إحدى العينتين في قاعدة البيانات.")
        print("    تأكد من إدخال السجلات أولاً أو تشغيل الخيار 3 أو 4 لتغذية البيانات.")


def main():
    # التهيئة الأولى لقاعدة البيانات وتحميل عينات تجريبية
    init_db()
    seed_sample_data()

    print("\n" + "=" * 65)
    print("   Gaza DNA Forensic Matcher & Sequencer Integration System   ")
    print("   نظام إدارة ومطابقة البصمات الجينية والتكامل مع أجهزة الفحص   ")
    print("=" * 65)

    while True:
        print("\nقائمة الخيارات الرئيسية:")
        print("  1. إجراء مطابقة فردية مباشرة (Direct Single Match)")
        print("  2. تشغيل محرك الفحص الشامل لقاعدة البيانات (Batch Matching)")
        print("  3. استيراد عينة مباشرة من جهاز تسلسل جيني (CODIS XML / FASTA)")
        print("  4. إدخال بصمة جينية (STR) يدوياً عبر الشاشة")
        print("  5. خروج")

        choice = input("\n[?] أدخل رقم الخيار (1-5): ").strip()

        if choice == '1':
            direct_single_match_ui()

        elif choice == '2':
            print("\n[*] جاري تشغيل محرك الفحص الآلي لمسح قاعدة البيانات والتطابق...")
            matches = run_batch_matching(threshold=50.0)
            
            if matches:
                print(f"\n[+] تم العثور على {len(matches)} مطابقة ناجحة (أعلى من 50%):")
                print("-" * 60)
                for idx, match in enumerate(matches, 1):
                    print(f"  {idx}. الرفات المشفر: {match['remains_code']} | العائلة المشفرة: {match['relative_code']} | التوافق: {match['percentage']}%")
                print("-" * 60)
            else:
                print("\n[-] لم يتم العثور على أي حالات توافق تتجاوز العتبة المحددة.")

        elif choice == '3':
            print("\n=== استيراد عينة من جهاز الفحص الجيني ===")
            sample_code = input("[?] أدخل رمز العينة/الرفات: ").strip()
            file_path = input("[?] أدخل مسار الملف الصادر من الجهاز (مثال: sample.xml أو sample.fasta): ").strip()
            file_type = input("[?] أدخل نوع الملف (codis / fasta): ").strip().lower()
            
            if not os.path.exists(file_path):
                print(f"[-] خطأ: الملف غير موجود في المسار: {file_path}")
                continue

            is_remains_input = input("[?] هل هذه العينة لرفات؟ (y/n, الافتراضي y): ").strip().lower()
            is_remains = False if is_remains_input == 'n' else True

            success = insert_sample_from_sequencer_file(sample_code, file_path, file_type, is_remains=is_remains)
            if success:
                print("\n[+] تم استيراد العينة وتخزينها بنجاح! يمكنك تشغيل الخيار (2) لمطابقتها فوراً.")

        elif choice == '4':
            interactive_dna_entry()

        elif choice == '5':
            print("\nتم إنهاء البرنامج بنجاح. دمتم بخير!")
            break

        else:
            print("\n[-] خيار غير صحيح، يرجى اختيار رقم من 1 إلى 5.")


if __name__ == "__main__":
    main()
