import sqlite3
import json
from modules.encryption import anonymize_id
from modules.dna_matcher import calculate_str_match

DB_NAME = "forensic_database.db"

def init_db():
    """إنشاء الجداول الرئيسية لقاعدة البيانات الجنائية المحلية"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # جدول الرفات المجهولة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_code TEXT UNIQUE,
            str_profile TEXT
        )
    ''')
    
    # جدول عائلات المفقودين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relative_code TEXT UNIQUE,
            str_profile TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_sample_data():
    """تعبئة قاعدة البيانات تلقائياً بمئات/مجموعات عينات تجريبية لاختبار الفحص الجماعي"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # عينات رفات تجريبية
    remains_samples = [
        ("KY-2026-081", {"D3S1358": [15, 18], "vWA": [14, 17], "FGA": [20, 24], "D8S1179": [12, 13], "D21S11": [28, 30]}),
        ("GZ-2026-102", {"D3S1358": [12, 14], "vWA": [15, 16], "FGA": [18, 22], "D8S1179": [10, 11], "D21S11": [25, 27]}),
        ("RFA-2026-044", {"D3S1358": [16, 17], "vWA": [13, 18], "FGA": [21, 23], "D8S1179": [14, 15], "D21S11": [30, 32]})
    ]
    
    # عينات أهالي مرجعية
    relatives_samples = [
        ("401234567", {"D3S1358": [15, 16], "vWA": [14, 18], "FGA": [20, 22], "D8S1179": [12, 14], "D21S11": [29, 31]}), # مطابقة مع العينة الأولى
        ("908765432", {"D3S1358": [11, 13], "vWA": [15, 17], "FGA": [18, 20], "D8S1179": [10, 12], "D21S11": [25, 28]})  # مطابقة مع العينة الثانية
    ]
    
    for sample_code, profile in remains_samples:
        enc_code = anonymize_id(sample_code)
        cursor.execute("INSERT OR IGNORE INTO remains (sample_code, str_profile) VALUES (?, ?)",
                       (enc_code, json.dumps(profile)))
                       
    for rel_code, profile in relatives_samples:
        enc_code = anonymize_id(rel_code)
        cursor.execute("INSERT OR IGNORE INTO relatives (relative_code, str_profile) VALUES (?, ?)",
                       (enc_code, json.dumps(profile)))
                       
    conn.commit()
    conn.close()

def run_batch_matching(threshold=70.0):
    """خوارزمية الفحص التلقائي الشامل (Batch Matching Engine) لمقارنة كل الرفات مع كل العائلات"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT sample_code, str_profile FROM remains")
    remains_list = cursor.fetchall()
    
    cursor.execute("SELECT relative_code, str_profile FROM relatives")
    relatives_list = cursor.fetchall()
    
    matches_found = []
    
    # خوارزمية المسح التلقائي المتعدد المتقاطع (Cross-Matching)
    for rem_code, rem_str in remains_list:
        rem_profile = json.loads(rem_str)
        for rel_code, rel_str in relatives_list:
            rel_profile = json.loads(rel_str)
            
            result = calculate_str_match(rem_profile, rel_profile)
            
            # فلترة النتائج ذات احتمالية التطابق العالية
            if result['match_percentage'] >= threshold:
                matches_found.append({
                    "remains_code": rem_code,
                    "relative_code": rel_code,
                    "percentage": result['match_percentage'],
                    "status": result['status']
                })
                
    conn.close()
    return matches_found

from modules.parser import parse_codis_xml, parse_fasta_str

def insert_sample_from_sequencer_file(sample_code: str, file_path: str, file_type: str, is_remains: bool = True):
    """
    استيراد البيانات الجينية مباشرة من ملفات أجهزة التسلسل وتحويلها وتخزينها في قاعدة البيانات.
    """
    if file_type.lower() == 'codis':
        profile = parse_codis_xml(file_path)
    elif file_type.lower() == 'fasta':
        profile = parse_fasta_str(file_path)
    else:
        print("[-] صيغة ملف غير مدعومة.")
        return False

    if not profile:
        print("[-] تعذر استخراج البصمة الجينية من الملف.")
        return False

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    enc_code = anonymize_id(sample_code)
    table = "remains" if is_remains else "relatives"
    col = "sample_code" if is_remains else "relative_code"
    
    cursor.execute(f"INSERT OR REPLACE INTO {table} ({col}, str_profile) VALUES (?, ?)",
                   (enc_code, json.dumps(profile)))
                   
    conn.commit()
    conn.close()
    print(f"[✓] تم استيراد وحفظ البصمة الجينية من ملف {file_type.upper()} بنجاح للعينة: {sample_code}")
    return True
