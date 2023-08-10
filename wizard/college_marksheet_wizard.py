# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import MissingError


class CollegeMarksheetWizard(models.TransientModel):
    """to add fields in Marksheet wizard."""
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
        """action for printing pdf"""
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
            inner join college_course as cco on cco.id = csm.course_id
            inner join college_academic_year as ay on ay.id= cc.academic_year_id
            """
            query += f"""where ce.type = '{self.exam_type}' and cm.students_id =
             '{self.student_id.id}'"""
            self.env.cr.execute(query)
            report = self.env.cr.dictfetchall()
            if not report:
                raise MissingError("Mark Sheet does not exist or this Student "
                                   "didn't take the exam.")
            data = {'report': report}
            return (self.env.ref(
                'college.college_marksheet_studentwise_report_view_action').
                    report_action(None, data=data))

        else:
            students = """select cm.students_id,cm.result,cm.total_mark,
            cm.total_max,cs.name,cc.name as class,cco.name as course,
            ay.name as academic_year,ce.type,ce.students_count as total
            from college_marksheet as cm
            inner join college_students as cs on cm.students_id = cs.id
            inner join college_exam as ce on cm.exam_id = ce.id
            inner join college_class as cc on ce.class_id = cc.id
            inner join college_semester as csm on cc.semester_id = csm.id
            inner join college_course as cco on csm.course_id = cco.id
            inner join college_academic_year as ay on cc.academic_year_id= ay.id
            """
            students += f"""where ce.type = '{self.exam_type}' and ce.class_id =
                                     '{self.class_id.id}'"""
            self.env.cr.execute(students)
            report = self.env.cr.dictfetchall()
            for record in report:
                paper = """select cm.students_id,cp.result,cp.obtained_mark,
                cs.subject,cs.pass_mark,ce.type
                from college_marksheet as cm
                inner join college_exam as ce on cm.exam_id = ce.id
                inner join college_papers as cp on cm.id = cp.marksheet_id
                inner join college_syllabus as cs on cp.subject_id = cs.id
                """
                paper += f"""where ce.type = '{self.exam_type}' and
                 cm.students_id = '{record['students_id']}' 
                 order by cm.students_id,cp.subject_id"""
                self.env.cr.execute(paper)
                rec = self.env.cr.dictfetchall()
                record['paper'] = rec
            if not report:
                raise MissingError("Mark Sheet does not exist or this")
            total = report[0]['total']
            pass_count = 0
            for rec in report:
                if rec['result']:
                    pass_count += 1
            fail_count = total - pass_count
            tp_total = total
            tp_pass = pass_count
            pl_fail = fail_count
            pl_pass = pass_count
            for rec in range(1, pass_count+1):
                if total % rec == 0 and pass_count % rec == 0:
                    tp_total = total / rec
                    tp_pass = pass_count / rec
            for rec in range(1, min(pass_count, fail_count)+1):
                if pass_count % rec == 0 and fail_count % rec == 0:
                    pl_fail = fail_count / rec
                    pl_pass = pass_count / rec
            tp_ratio = f"{int(tp_total)}:{int(tp_pass)}"
            pl_ratio = f"{int(pl_pass)}:{int(pl_fail)}"
            ratio = [{'pl_ratio': pl_ratio, 'tp_ratio': tp_ratio}]
            count = [{'total': total, 'pass': pass_count, 'fail': fail_count}]
            data = {'report': report,
                    'count': count,
                    'ratio': ratio}
            return (self.env.ref(
                'college.college_marksheet_classwise_report_view_action').
                    report_action(None, data=data))
