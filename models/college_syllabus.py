# -*- coding: utf-8 -*-
from odoo import fields, models


class CollegeSyllabus(models.Model):
    """This is used to add syllabus and its features"""
    _name = "college.syllabus"
    _description = "College Syllabus"
    _rec_name = "subject"

    subject = fields.Char(copy=False)
    max_mark = fields.Integer(string="Maximum Mark")
    pass_mark = fields.Float(string="Pass Mark")
    semester_id = fields.Many2one("college.semester")
