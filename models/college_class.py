# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CollegeClass(models.Model):
    """This is used to set class."""
    _name = "college.class"
    _description = "College Class"

    name = fields.Char(compute="_compute_name", copy=False, default="Name",
                       store=True)
    semester_id = fields.Many2one("college.semester",
                                  "Semester", required=True)
    course_id = fields.Many2one("college.course",
                                related="semester_id.course_id",
                                string="Course")
    academic_year_id = fields.Many2one("college.academic.year", "Academic Year",
                                       required=True)
    students_ids = fields.One2many("college.students", "class_id")
    promotion_id = fields.Many2one("college.class", string="Promotion Class")

    @api.constrains('semester_id', 'academic_year_id')
    def _compute_name(self):
        """to generate class name"""
        for record in self:
            record.name = f"{str(record.semester_id.name)} " \
                          f"{str(record.academic_year_id.name)}"

    @api.constrains('semester_id', 'academic_year_id')
    def check_class_existence(self):
        """this function to block creating class, if that class
        already created."""
        for record in self:
            existing_class = record.search([
                ('semester_id', '=', record.semester_id.id),
                ('academic_year_id', '=', record.academic_year_id.id)
            ])
        if len(existing_class) > 1:
            raise ValidationError("Class already exist")
