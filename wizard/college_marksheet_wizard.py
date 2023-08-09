from odoo import api, fields, models


class CollegeMarksheetWizard(models.TransientModel):
    _name = 'college.marksheet.wizard'

    report_type = fields.Selection(selection=[('student_wise', 'Student Wise'),
                                              ('class_wise', 'Class Wise')],
                                   required=True, default='student_wise')
    student_id = fields.Many2one('college.students', string='Student')
    class_id = fields.Many2one('college.class', string="Class")
    semester_id = fields.Many2one('college.semester', string="Semester",
                                  readonly=True)
    exam_type = fields.Selection(selection=[('internal_exam', 'Internal Exam'),
                                            ('semester_exam', 'Semester Exam'),
                                            ('unit_test', 'Unit Test')],
                                 required=True)

    @api.onchange('student_id', 'class_id')
    def _onchange_semester(self):
        if self.report_type == 'student_wise' and self.student_id:
            self.semester_id = self.student_id.semester_id.id
        elif self.report_type == 'class_wise' and self.class_id:
            self.semester_id = self.class_id.semester_id.id

    def print_pdf(self):
        if self.report_type == 'student_wise':
            query = """select cst.name,cco.name as course,
            ay.name as academic_year,ce.type,cm.result,cs.pass_mark,
            cs.subject,cp.obtained_mark,cp.result as pass_fail
            from college_marksheet as cm
            inner join college_papers as cp on cp.marksheet_id = cm.id
            inner join college_syllabus as cs on cs.id = cp.subject_id
            inner join college_exam as ce on ce.id = cm.exam_id
            inner join college_class as cc on cc.id = ce.class_id
            inner join college_semester as csm on csm.id = cc.semester_id
            inner join college_students as cst on cst.id = cm.students_id
            inner join college_course as cco on cco.id = ce.class_id
            inner join college_academic_year as ay on ay.id= cc.academic_year_id
            """
            query += f"""where ce.type = '{self.exam_type}' and cm.students_id =
             '{self.student_id.id}'"""
            self.env.cr.execute(query)
            report = self.env.cr.dictfetchall()
            # print(report)
            data = {'report': report}
            return self.env.ref(
                'college.college_marksheet_studentwise_report_view_action').report_action(None, data=data)

        else:
            print('class')
            return self.env.ref(
                'college.college_marksheet_classwise_report_view_action'). \
                report_action(self)
