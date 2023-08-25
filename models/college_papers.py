# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CollegePapers(models.Model):
    """this is used to set exam papers"""
    _name = "college.papers"
    _description = "College Exam Papers"

    subject_id = fields.Many2one("college.syllabus", string="Subject")
    pass_mark = fields.Float(copy=False, related="subject_id.pass_mark")
    obtained_mark = fields.Float(copy=False)
    max_mark = fields.Integer(string="Maximum Mark",
                              related="subject_id.max_mark")
    result = fields.Boolean(string="Pass/Fail", readonly=True)
    exam_id = fields.Many2one("college.exam")
    marksheet_id = fields.Many2one("college.marksheet")

    @api.constrains('obtained_mark')
    def check_pass_or_fail(self):
        """for toggle button to show the result is passed or failed"""
        self.result = True if self.obtained_mark >= self.pass_mark else False

    @api.constrains('obtained_mark')
    def mark_validation(self):
        """this for mark validation. If obtained mark is above Maximum mark,
        then warning message will appear."""
        for record in self:
            if record.obtained_mark:
                if record.obtained_mark > record.max_mark:
                    raise ValidationError("Invalid Mark Entered")
