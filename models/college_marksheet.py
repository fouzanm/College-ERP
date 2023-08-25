# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CollegeMarkSheet(models.Model):
    """this used to set mark sheet"""
    _name = 'college.marksheet'
    _description = 'College Exam Mark Sheet'
    _rec_name = "students_id"

    students_id = fields.Many2one("college.students", string="Student")
    exam_id = fields.Many2one('college.exam', string="Exam",
                              readonly=True)
    class_id = fields.Many2one('college.class', string="Class",
                               related="exam_id.class_id")
    course_id = fields.Many2one('college.course', string="Course",
                                related="exam_id.course_id")
    semester_id = fields.Many2one('college.semester', string="Semester",
                                  related="exam_id.semester_id")
    result = fields.Boolean(string="Pass/Fail", compute="_compute_result",
                            readonly=True, store=True)
    total_mark = fields.Float(compute='_compute_total_mark', store=True)
    rank = fields.Integer(compute='_compute_rank', default=0)
    papers_ids = fields.One2many("college.papers", "marksheet_id")
    total_max = fields.Integer(string="Max Total", store=True)
    promoted_students_id = fields.Many2one("college.promotion")


    @api.depends('papers_ids')
    def _compute_total_mark(self):
        """this function to calculate total obtained mark and total mark."""
        for record in self:
            total_mark = 0
            max_mark = 0
            for rec in record.papers_ids:
                total_mark += rec.obtained_mark
                max_mark += rec.max_mark
            record.total_mark = total_mark
            record.total_max = max_mark

    @api.depends('total_mark')
    def _compute_rank(self):
        """this function for set rank based on total mark obtained in exam."""
        for record in self:
            students = record.search([
                ('exam_id', '=', record.exam_id.id)])
            record.rank = 0
        mark_list = {}
        for record in students:
            mark_list[record] = record.total_mark
        mark_list = sorted(mark_list.items(), key=lambda x: x[1])
        mark_list.reverse()
        rank = 1
        for record in mark_list:
            record[0].rank = rank
            rank += 1

    @api.depends('papers_ids')
    def _compute_result(self):
        """this for toggle button to view the result is pass or fail."""
        for record in self.papers_ids:
            if record.result is not False:
                self.result = True
            else:
                self.result = False
                break
