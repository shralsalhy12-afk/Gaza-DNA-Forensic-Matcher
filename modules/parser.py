import xml.etree.ElementTree as ET
import re

def parse_codis_xml(file_path: str) -> dict:
    """
    محلل ملفات CODIS XML الجنائية.
    يقوم باستخراج المواقع الجينية (Loci) وقيم الأليلات (Alleles) لكل موقع.
    """
    str_profile = {}
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # البحث عن كافة عناصر Locus داخل ملف الـ XML
        for locus in root.findall('.//Locus'):
            locus_name = locus.find('LocusName')
            if locus_name is not None and locus_name.text:
                name = locus_name.text.strip()
                alleles = []
                
                # استخراج جميع الأليلات التابعة لهذا الموقع
                for allele in locus.findall('.//AlleleCall'):
                    if allele.text:
                        try:
                            # تحويل القيمة إلى رقم (float لتغطية الأليلات الكسرية مثل 9.3)
                            val = float(allele.text.strip())
                            alleles.append(val)
                        except ValueError:
                            continue
                            
                if alleles:
                    str_profile[name] = alleles

        return str_profile
    except Exception as e:
        print(f"[-] خطأ أثناء قراءة ملف CODIS XML: {e}")
        return {}


def parse_fasta_str(file_path: str, target_loci_motifs: dict = None) -> dict:
    """
    محلل ملفات FASTA التسلسلية الخام (NGS Sequencing).
    يقوم بحساب عدد التكرارات المتتالية (STR Repeats) بناءً على النمط النيوكليوتيدي (Motif).
    """
    if target_loci_motifs is None:
        # القوالب النيوكليوتيدية القياسية لبعض المواقع الجينية الشهيرة
        target_loci_motifs = {
            "D3S1358": "TCTA",
            "vWA": "TCTA",
            "FGA": "CTTT",
            "TH01": "AATG",
            "D21S11": "TCTA"
        }

    str_profile = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # دمج سلاسل ה- DNA واشتراط إزالة الترويسة
        sequence = "".join([line.strip() for line in lines if not line.startswith(">")]).upper()

        for locus, motif in target_loci_motifs.items():
            # خوارزمية التعابير النمطية (Regex) لإيجاد أطول تكرار متتالي للنمط
            pattern = f"(?:{motif})+"
            matches = re.findall(pattern, sequence)
            
            if matches:
                # حساب أعداد التكرار للأليلات المكتشفة
                repeat_counts = sorted(list(set([len(m) // len(motif) for m in matches])), reverse=True)
                # أخذ أعلى أليلين مميزين (بصمة ثنائية - Diploid)
                str_profile[locus] = repeat_counts[:2]

        return str_profile
    except Exception as e:
        print(f"[-] خطأ أثناء تحليل ملف FASTA: {e}")
        return {}
