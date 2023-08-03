# -*- coding: utf-8 -*-
{
    'name': 'College',
    'version': '16.0.1.0.0',
    'category': 'Extra',
    'summary': 'College Details',
    'description': 'College ERP',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/college_admission_email.xml',
        'data/college_admission_number.xml',
        'views/college_students.xml',
        'views/college_course.xml',
        'views/college_semester.xml',
        'views/college_syllabus.xml',
        'views/college_academic_year.xml',
        'views/college_admission.xml',
        'views/college_class.xml',
        'views/college_exam.xml',
        'views/college_papers.xml',
        'views/college_marksheet.xml',
        'views/college_promotion.xml',
        'views/college_menus.xml',
    ],
    'application': True
}