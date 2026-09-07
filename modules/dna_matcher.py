def calculate_str_match(sample_str: dict, reference_str: dict) -> dict:
    """
    مقارنة علامات الـ STR بين عينة الرفات وعينة المرجع (أقارب المفقود)
    لحساب عدد المواقع الجينية المتطابقة وتحديد نسبة الاحتمالية الجنائية.
    """
    total_loci = len(sample_str)
    if total_loci == 0:
        return {"matching_loci": 0, "total_loci": 0, "match_percentage": 0.0, "status": "Inconclusive"}

    matching_loci = 0
    mismatches = []

    for locus, alleles in sample_str.items():
        if locus in reference_str:
            ref_alleles = reference_str[locus]
            # التحقق من وجود أليل مشترك على الأقل (مطابقة قرابة درجة أولى)
            if set(alleles).intersection(set(ref_alleles)):
                matching_loci += 1
            else:
                mismatches.append(locus)

    match_percentage = round((matching_loci / total_loci) * 100, 2)

    # التقييم الطب الشرعي الجنائي
    if match_percentage >= 90.0:
        status = "High Probability Kinship Match (مطابقة قرابة مؤكدة)"
    elif match_percentage >= 70.0:
        status = "Moderate Match - Requires Secondary Testing (مطابقة محتملة)"
    else:
        status = "Excluded / No Kinship (استبعاد مطابقة)"

    return {
        "matching_loci": matching_loci,
        "total_loci": total_loci,
        "match_percentage": match_percentage,
        "mismatches": mismatches,
        "status": status
    }
