import sqlite3
import json
from modules.encryption import anonymize_id
from modules.dna_matcher import calculate_str_match
from modules.parser import parse_codis_xml, parse_fasta_str

DB_NAME = "forensic_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_code TEXT UNIQUE,
            str_profile TEXT
        )
    ''')
    
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    sample_remains = [
        ("REF-2026-001", {"D3S1358": [15, 18], "vWA": [14, 17], "FGA": [21, 24], "TH01": [6, 9.3]}),
        ("REF-2026-002", {"D3S1358": [12, 16], "vWA": [15, 18], "FGA": [20, 22], "TH01": [7, 9]})
    ]

    sample_relatives = [
        ("FAM-PAL-101", {"D3S1358": [15, 17], "vWA": [14, 16], "FGA": [21, 25], "TH01": [6, 8]}), # نسبة مطابقة عالية جداً
        ("FAM-PAL-102", {"D3S1358": [11, 14], "vWA": [12, 15], "FGA": [19, 23], "TH01": [5, 7]})  # نسبة مطابقة منخفضة
    ]

    for code, profile in sample_remains:
        enc_code = anonymize_id(code)
        cursor.execute("INSERT OR IGNORE INTO remains (sample_code, str_profile) VALUES (?, ?)",
                       (enc_code, json.dumps(profile)))

    for code, profile in sample_relatives:
        enc_code = anonymize_id(code)
        cursor.execute("INSERT OR IGNORE INTO relatives (relative_code, str_profile) VALUES (?, ?)",
                       (enc_code, json.dumps(profile)))

    conn.commit()
    conn.close()


def insert_sample_from_sequencer_file(sample_code: str, file_path: str, file_type: str, is_remains: bool = True) -> bool:
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
    
    try:
        cursor.execute(f"INSERT OR REPLACE INTO {table} ({col}, str_profile) VALUES (?, ?)",
                       (enc_code, json.dumps(profile)))
        conn.commit()
        print(f"[✓] تم استيراد وحفظ البصمة الجينية من ملف {file_type.upper()} بنجاح للعينة: {sample_code}")
        return True
    except Exception as e:
        print(f"[-] خطأ أثناء الحفظ في قاعدة البيانات: {e}")
        return False
    finally:
        conn.close()


def run_batch_matching(threshold: float = 50.0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT sample_code, str_profile FROM remains")
    remains_list = cursor.fetchall()

    cursor.execute("SELECT relative_code, str_profile FROM relatives")
    relatives_list = cursor.fetchall()

    matches = []

    for rem_code, rem_str in remains_list:
        rem_profile = json.loads(rem_str)
        
        for rel_code, rel_str in relatives_list:
            rel_profile = json.loads(rel_str)
            
            score = calculate_str_match(rem_profile, rel_profile)
            
            if score >= threshold:
                matches.append({
                    "remains_code": rem_code,
                    "relative_code": rel_code,
                    "percentage": round(score, 2)
                })

    conn.close()
    return matches
