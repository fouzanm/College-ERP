# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CollegeSemester(models.Model):
    """This is used to add semester and its features"""
    _name = 'college.semester'
    _description = 'College Course Details'

    name = fields.Char(string="Semester Name", compute="_compute_name")
    sem_no = fields.Integer(string="Semester No")
    course_id = fields.Many2one("college.course", "Course")
    class_id = fields.Many2one("college.class")
    syllabus_ids = fields.One2many("college.syllabus", "semester_id")

    @api.depends('sem_no', 'course_id')
    def _compute_name(self):
        """to generate semester name"""
        for record in self:
            record.name = \
                f"{str(record.sem_no)} Sem: {str(record.course_id.name)}"
