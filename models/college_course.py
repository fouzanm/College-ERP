# -*- coding: utf-8 -*-
from odoo import fields, models


class CollegeCourse(models.Model):
    """This is used to add course and its features"""
    _name = "college.course"
    _description = "Course Details"

    name = fields.Char(string="Course")
    category = fields.Selection(selection=[('ug', 'UG'), ('pg', 'PG'),
                                           ('diploma', 'diploma')])
    duration = fields.Integer(string="Duration")
    no_of_sem = fields.Integer(string="No of Semester")
    semester_ids = fields.One2many("college.semester", 'course_id')
