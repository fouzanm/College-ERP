# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import MissingError
import json
import io
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class CollegeMarksheetWizard(models.TransientModel):
    """to add fields in Marksheet wizard."""
    _name = 'college.marksheet.wizard'
    _description = 'College Marksheet Wizard'

    report_type = fields.Selection(selection=[('student_wise', 'Student Wise'),
                                              ('class_wise', 'Class Wise')],
                                   required=True, default='student_wise')
    student_id = fields.Many2one('college.students',
                                 string='Student')
    class_id = fields.Many2one('college.class', string="Class")
    semester_id = fields.Many2one('college.semester', readonly=True,
                                  string="Semester", store=True,
                                  compute="_compute_semester")
    exam_type = fields.Selection(selection=[('internal_exam', 'Internal Exam'),
                                            ('semester_exam', 'Semester Exam'),
                                            ('unit_test', 'Unit Test')],
                                 required=True)

    @api.depends('student_id', 'class_id')
    def _compute_semester(self):
        for record in self:
            if record.report_type == 'student_wise' and record.student_id:
                record.semester_id = record.student_id.semester_id.id
            elif record.report_type == 'class_wise' and record.class_id:
                record.semester_id = record.class_id.semester_id.id

    def print_pdf(self):
        """action for printing pdf"""
        if self.report_type == 'student_wise':
            query = f"""select cst.name,cco.name as course,
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
            where ce.type = '{self.exam_type}' and cm.students_id =
             '{self.student_id.id}'
            """
            self.env.cr.execute(query)
            report = self.env.cr.dictfetchall()
            for record in report:
                record['type'] = record['type'].replace("_", " ").title()
            if not report:
                raise MissingError("Mark Sheet does not exist or this Student "
                                   "didn't take the exam.")
            data = {'report': report}
            return (self.env.ref(
                'college.college_marksheet_studentwise_report_view_action').
                    report_action(None, data=data))

        else:
            students = f"""select cm.students_id,cm.result,cm.total_mark,
            cm.total_max,cs.name,cc.name as class,cco.name as course,
            ay.name as academic_year,ce.type,ce.students_count as total
            from college_marksheet as cm
            inner join college_students as cs on cm.students_id = cs.id
            inner join college_exam as ce on cm.exam_id = ce.id
            inner join college_class as cc on ce.class_id = cc.id
            inner join college_semester as csm on cc.semester_id = csm.id
            inner join college_course as cco on csm.course_id = cco.id
            inner join college_academic_year as ay on cc.academic_year_id= ay.id
            where ce.type = '{self.exam_type}' and ce.class_id =
                                     '{self.class_id.id}'
            """
            self.env.cr.execute(students)
            report = self.env.cr.dictfetchall()
            for record in report:
                paper = f"""select cm.students_id,cp.result,cp.obtained_mark,
                cs.subject,cs.pass_mark,ce.type
                from college_marksheet as cm
                inner join college_exam as ce on cm.exam_id = ce.id
                inner join college_papers as cp on cm.id = cp.marksheet_id
                inner join college_syllabus as cs on cp.subject_id = cs.id
                where ce.type = '{self.exam_type}' and
                 cm.students_id = '{record['students_id']}' 
                 order by cm.students_id,cp.subject_id
                """
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
            for rec in range(1, pass_count + 1):
                if total % rec == 0 and pass_count % rec == 0:
                    tp_total = total / rec
                    tp_pass = pass_count / rec
            for rec in range(1, min(pass_count, fail_count) + 1):
                if pass_count % rec == 0 and fail_count % rec == 0:
                    pl_fail = fail_count / rec
                    pl_pass = pass_count / rec
            tp_ratio = f"{int(tp_total)}:{int(tp_pass)}"
            pl_ratio = f"{int(pl_pass)}:{int(pl_fail)}"
            ratio = [{'pl_ratio': pl_ratio, 'tp_ratio': tp_ratio}]
            count = [{'total': total, 'pass': pass_count, 'fail': fail_count}]
            for record in report:
                record['type'] = record['type'].replace("_", " ").title()
            data = {'report': report,
                    'count': count,
                    'ratio': ratio}
            return (self.env.ref(
                'college.college_marksheet_classwise_report_view_action').
                    report_action(None, data=data))

    def print_xlsx(self):
        if self.report_type == 'student_wise':
            query = f"""
                    select cst.name,cco.name as course,
                    ay.name as academic_year,ce.type,cm.result,cs.pass_mark,
                    cs.subject,cp.obtained_mark,cp.result as pass_fail
                    from college_marksheet as cm
                    inner join college_papers as cp on cp.marksheet_id = cm.id
                    inner join college_syllabus as cs on cs.id = cp.subject_id
                    inner join college_exam as ce on ce.id = cm.exam_id
                    inner join college_class as cc on cc.id = ce.class_id
                    inner join college_semester as csm on csm.id= cc.semester_id
                    inner join college_students as cst on cst.id= cm.students_id
                    inner join college_course as cco on cco.id = csm.course_id
                    inner join college_academic_year as ay 
                    on ay.id= cc.academic_year_id
                    where ce.type = '{self.exam_type}' and cm.students_id =
                         '{self.student_id.id}'
                    """
            self.env.cr.execute(query)
            report = self.env.cr.dictfetchall()
            data = {'report': report,
                    'report_type': self.report_type}
            if not data['report']:
                raise MissingError("Mark Sheet does not exist or this Student "
                                   "didn't take the exam.")
            return {
                'type': 'ir.actions.report',
                'data': {'model': 'college.marksheet.wizard',
                         'options': json.dumps(data,
                                               default=date_utils.json_default),
                         'output_format': 'xlsx',
                         'report_name': 'Student Marksheet',
                         },
                'report_type': 'marksheet_xlsx',
            }
        else:
            students = f"""select cm.students_id,cm.result,cm.total_mark,
                        cm.total_max,cs.name,cc.name as class,cco.name as course
                        ,ay.name as academic_year,ce.type,ce.students_count as 
                        total from college_marksheet as cm
                        inner join college_students as cs on
                         cm.students_id = cs.id
                        inner join college_exam as ce on cm.exam_id = ce.id
                        inner join college_class as cc on ce.class_id = cc.id
                        inner join college_semester as csm on
                         cc.semester_id = csm.id
                        inner join college_course as cco on 
                        csm.course_id = cco.id
                        inner join college_academic_year as ay on 
                        cc.academic_year_id = ay.id
                        where ce.type = '{self.exam_type}' and ce.class_id =
                                                 '{self.class_id.id}'
                        """
            self.env.cr.execute(students)
            report = self.env.cr.dictfetchall()
            for record in report:
                paper = f"""select cm.students_id,cp.result,cp.obtained_mark,
                            cs.subject,cs.pass_mark,ce.type
                            from college_marksheet as cm
                            inner join college_exam as ce on cm.exam_id = ce.id
                            inner join college_papers as cp on
                             cm.id = cp.marksheet_id
                            inner join college_syllabus as cs on
                             cp.subject_id = cs.id
                            where ce.type = '{self.exam_type}' and
                            cm.students_id = '{record['students_id']}' 
                            order by cm.students_id,cp.subject_id
                            """
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
            for rec in range(1, pass_count + 1):
                if total % rec == 0 and pass_count % rec == 0:
                    tp_total = total / rec
                    tp_pass = pass_count / rec
            for rec in range(1, min(pass_count, fail_count) + 1):
                if pass_count % rec == 0 and fail_count % rec == 0:
                    pl_fail = fail_count / rec
                    pl_pass = pass_count / rec
            tp_ratio = f"{int(tp_total)}:{int(tp_pass)}"
            pl_ratio = f"{int(pl_pass)}:{int(pl_fail)}"
            ratio = [{'pl_ratio': pl_ratio, 'tp_ratio': tp_ratio}]
            count = [{'total': total, 'pass': pass_count, 'fail': fail_count}]
            data = {'report': report,
                    'count': count,
                    'ratio': ratio,
                    'report_type': self.report_type}
            return {
                'type': 'ir.actions.report',
                'data': {'model': 'college.marksheet.wizard',
                         'options': json.dumps(data,
                                               default=date_utils.json_default),
                         'output_format': 'xlsx',
                         'report_name': 'Class Report',
                         },
                'report_type': 'marksheet_xlsx',
            }

    def get_xlsx_report(self, data, response):
        if data['report_type'] == 'student_wise':
            name = data['report'][0]['name']
            course = data['report'][0]['course']
            academic_year = data['report'][0]['academic_year']
            exam = data['report'][0]['type'].replace("_", " ").title()
            result = data['report'][0]['result']
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet()
            cell_format = workbook.add_format(
                {'font_size': '12px', 'align': 'center'})
            head = workbook.add_format(
                {'align': 'center', 'bold': True, 'font_size': '20px'})
            txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
            sheet.merge_range('B2:I3', 'Student wise Marksheet', head)
            sheet.merge_range('A6:B6', 'Name:', cell_format)
            sheet.merge_range('C6:D6', name, txt)
            sheet.merge_range('A7:B7', 'Course:', cell_format)
            sheet.merge_range('C7:D7', course, txt)
            sheet.merge_range('A8:B8', 'Academic Year:', cell_format)
            sheet.merge_range('C8:D8', academic_year, txt)
            sheet.merge_range('A9:B9', 'Exam Type:', cell_format)
            sheet.merge_range('C9:D9', exam, txt)
            sheet.merge_range('A10:B10', 'Result:', cell_format)
            if result is True:
                sheet.merge_range('C10:D10', 'Pass', txt)
            else:
                sheet.merge_range('C10:D10', 'Fail', txt)
            sheet.merge_range('A12:B12', 'Subject', cell_format)
            sheet.merge_range('C12:D12', 'Obtained Mark', cell_format)
            sheet.merge_range('E12:F12', 'Pass Mark', cell_format)
            sheet.merge_range('G12:H12', 'Pass / Fail', cell_format)
            line = 13
            for record in data['report']:
                subject = record['subject']
                obtained_mark = record['obtained_mark']
                pass_mark = record['pass_mark']
                sheet.merge_range(f'A{line}:B{line}', subject, txt)
                sheet.merge_range(f'C{line}:D{line}', obtained_mark, txt)
                sheet.merge_range(f'E{line}:F{line}', pass_mark, txt)
                if result is True:
                    sheet.merge_range(f'G{line}:H{line}', 'Pass', txt)
                else:
                    sheet.merge_range(f'G{line}:H{line}', 'Fail', txt)
                line += 1
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()
        else:
            class_name = data['report'][0]['class']
            course = data['report'][0]['course']
            exam = data['report'][0]['type'].replace("_", " ").title()
            academic_year = data['report'][0]['academic_year']
            total = data['report'][0]['total']
            pass_count = data['count'][0]['pass']
            fail_count = data['count'][0]['fail']
            tp_ratio = data['ratio'][0]['tp_ratio']
            pl_ratio = data['ratio'][0]['pl_ratio']
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet()
            cell_format = workbook.add_format(
                {'font_size': '12px', 'align': 'center'})
            head = workbook.add_format(
                {'align': 'center', 'bold': True, 'font_size': '20px'})
            txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
            sheet.merge_range('B2:I3', 'Class wise Marksheet', head)
            sheet.merge_range('A6:B6', 'Class:', cell_format)
            sheet.merge_range('C6:D6', class_name, txt)
            sheet.merge_range('A7:B7', 'Course:', cell_format)
            sheet.merge_range('C7:D7', course, txt)
            sheet.merge_range('A8:B8', 'Academic Year:', cell_format)
            sheet.merge_range('C8:D8', academic_year, txt)
            sheet.merge_range('A9:B9', 'Exam Type:', cell_format)
            sheet.merge_range('C9:D9', exam, txt)
            sheet.merge_range('A10:B10', 'Total Students:', cell_format)
            sheet.merge_range('C10:D10', total, txt)
            sheet.merge_range('A11:B11', 'Pass:', cell_format)
            sheet.merge_range('C11:D11', pass_count, txt)
            sheet.merge_range('A12:B12', 'Fail:', cell_format)
            sheet.merge_range('C12:D12', fail_count, txt)
            sheet.merge_range('A13:B13', 'Total-Pass Ratio:', cell_format)
            sheet.merge_range('C13:D13', tp_ratio, txt)
            sheet.merge_range('A14:B14', 'Pass-Fail Ratio:', cell_format)
            sheet.merge_range('C14:D14', pl_ratio, txt)
            sheet.merge_range('A16:B16', 'Name', cell_format)
            col = 2
            row = 15
            for rec in data['report'][0]['paper']:
                sheet.merge_range(row, col, row, col+1, rec['subject'],
                                  cell_format)
                col += 2
            sheet.merge_range(row, col, row, col+1, 'Obtained Mark',
                              cell_format)
            sheet.merge_range(row, col+2, row, col+3, 'Total Mark', cell_format)
            sheet.merge_range(row, col+4, row, col+5, 'Pass / Failed',
                              cell_format)
            row = 16
            for record in data['report']:
                sheet.merge_range(f'A{row+1}:B{row+1}', record['name'], txt)
                col = 2
                for rec in record['paper']:
                    sheet.merge_range(row, col, row, col+1,
                                      rec['obtained_mark'], txt)
                    col += 2
                sheet.merge_range(row, col, row, col+1,
                                  record['total_mark'], txt)
                sheet.merge_range(row, col+2, row, col+3,
                                  record['total_max'], txt)
                if record['result'] is True:
                    sheet.merge_range(row, col+4, row, col+5, 'Pass', txt)
                else:
                    sheet.merge_range(row, col+6, row, col+7, 'Fail', txt)
                row += 1
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()
