# -*- coding: utf-8 -*-
{
    'name': 'College',
    'version': '16.0.1.0.0',
    'category': 'Extra',
    'summary': 'College Details',
    'description': 'College ERP',
    'author': 'Fouzan M',
    'depends': ['base', 'mail', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/college_admission_email.xml',
        'data/college_admission_number.xml',
        'data/college_exam_cron_scheduler.xml',
        'data/college_online_admission.xml',
        'data/college_admitted_list.xml',
        'views/college_students.xml',
        'views/college_course.xml',
        'views/college_semester.xml',
        'views/college_syllabus.xml',
        'views/college_academic_year.xml',
        'views/college_admission.xml',
        'views/college_class.xml',
        'views/college_exam.xml',
        'views/college_papers.xml',
        'views/college_promotion.xml',
        'views/college_marksheet.xml',
        'views/college_admission_template.xml',
        'views/college_admitted_list_template.xml',
        'wizard/college_marksheet_wizard.xml',
        'report/college_marksheet_studentwise_report.xml',
        'report/college_marksheet_studentwise_template.xml',
        'report/college_marksheet_classwise_report.xml',
        'report/college_marksheet_classwise_template.xml',
        'views/college_menus.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'college/static/src/js/action_manager.js',
            ],
            'web.assets_frontend': [
                'college/static/src/js/website_admission.js',
            ]
        },
    'application': True,
    'license': 'LGPL-3'
}
