def generate_xml():
    xml = ['<?xml version="1.0" encoding="utf-8"?>']
    xml.append('<odoo>')
    xml.append('    <data noupdate="1">')

    # Categories
    xml.append('        <!-- Categories -->')
    xml.append('        <record id="cat_primary" model="school.service.category"><field name="name">الابتدائي</field></record>')
    xml.append('        <record id="cat_middle" model="school.service.category"><field name="name">المتوسط</field></record>')
    xml.append('        <record id="cat_high" model="school.service.category"><field name="name">الثانوي</field></record>\n')

    # Primary
    xml.append('        <!-- Primary -->')
    xml.append('        <record id="sub_prim_general" model="school.service.subcategory"><field name="name">الابتدائي الطور</field><field name="category_id" ref="cat_primary"/></record>')
    for subj, code in [('اللغة العربية', 'ar'), ('اللغة الفرنسية', 'fr'), ('الرياضيات', 'math')]:
        xml.append(f'        <record id="course_prim_{code}" model="school.course"><field name="name">{subj}</field><field name="subcategory_id" ref="sub_prim_general"/><field name="is_published" eval="True"/></record>')

    # Middle
    xml.append('\n        <!-- Middle -->')
    mid_years = [('1 متوسط', '1'), ('2 متوسط', '2'), ('3 متوسط', '3'), ('4 متوسط', '4')]
    mid_subjects = [('الرياضيات', 'math'), ('العلوم الفيزيائية', 'phys'), ('علوم الطبيعة والحياة', 'sci'), ('اللغة العربية', 'ar'), ('اللغة الفرنسية', 'fr'), ('اللغة الإنجليزية', 'en')]
    for y_name, y_code in mid_years:
        xml.append(f'        <record id="sub_mid_{y_code}" model="school.service.subcategory"><field name="name">{y_name}</field><field name="category_id" ref="cat_middle"/></record>')
        for s_name, s_code in mid_subjects:
            xml.append(f'        <record id="course_mid_{y_code}_{s_code}" model="school.course"><field name="name">{s_name}</field><field name="subcategory_id" ref="sub_mid_{y_code}"/><field name="is_published" eval="True"/></record>')

    # High
    xml.append('\n        <!-- High -->')
    year1_branches = [('جذع مشترك آداب', 'y1b1'), ('جذع مشترك علوم', 'y1b2')]
    year23_branches = [('آداب وفلسفة', 'b1'), ('آداب ولغات', 'b2'), ('علوم تجريبية', 'b3'), ('رياضيات / تقني رياضي', 'b4'), ('تسيير واقتصاد', 'b5')]
    
    high_subs = []
    # 1st Year
    for b_name, b_code in year1_branches:
        high_subs.append((f'1 ثانوي - {b_name}', b_code))
    # 2nd Year
    for b_name, b_code in year23_branches:
        high_subs.append((f'2 ثانوي - {b_name}', f'y2{b_code}'))
    # 3rd Year
    for b_name, b_code in year23_branches:
        high_subs.append((f'3 ثانوي - {b_name}', f'y3{b_code}'))

    high_subjects = [('الرياضيات', 'math'), ('العلوم الفيزيائية', 'phys'), ('علوم الطبيعة والحياة', 'sci')]
    
    for s_name, s_code in high_subs:
        xml.append(f'        <record id="sub_high_{s_code}" model="school.service.subcategory"><field name="name">{s_name}</field><field name="category_id" ref="cat_high"/></record>')
        for subj_name, subj_code in high_subjects:
            xml.append(f'        <record id="course_high_{s_code}_{subj_code}" model="school.course"><field name="name">{subj_name}</field><field name="subcategory_id" ref="sub_high_{s_code}"/><field name="is_published" eval="True"/></record>')

    xml.append('    </data>')
    xml.append('</odoo>')

    with open(r'f:\projects\deploily-odoo\src\school_management_dz\data\algerian_school_data.xml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml))

generate_xml()
