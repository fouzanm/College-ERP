# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class CollegeStudents(models.Model):
    """This is used to view students and their details"""
    _name = "college.students"
    _description = "College Students"
    _inherit = 'mail.thread', 'mail.activity.mixin'

    name = fields.Char(compute="_compute_name", store=True)
    ad_no = fields.Char(string="Admission No:", readonly=True)
    ad_date = fields.Date(string="Admission Date")
    f_name = fields.Char(default="", required=True, string="First Name")
    l_name = fields.Char(default="", required=True, string="Last Name")
    father = fields.Char(string="Father's Name")
    mother = fields.Char(string="Mother's Name")
    communication_address = fields.Text(copy=False)
    permanent_address = fields.Text(copy=False)
    same_address = fields.Boolean(string="Same as Communication Address")
    phone = fields.Char(string="Phone No")
    email = fields.Char(copy=False)
    course_id = fields.Many2one("college.course", "Course",
                                related="semester_id.course_id")
    academic_year_id = fields.Many2one("college.academic.year",
                                       related="class_id.academic_year_id")
    class_id = fields.Many2one("college.class")
    semester_id = fields.Many2one("college.semester", "Semester",
                                  related="class_id.semester_id")

    @api.depends('f_name', 'l_name')
    def _compute_name(self):
        """this function is used concatenate first name
        and last name to find full name."""
        for record in self:
            record.name = f"{str(record.f_name)} {str(record.l_name)}"

    @api.model
    def create(self, vals):
        """to create admission number"""
        if vals.get('ad_no', _('New')) == _('New'):
            vals['ad_no'] = self.env['ir.sequence'].next_by_code(
                'college.admission.number') or _('New')
        res = super(CollegeStudents, self).create(vals)
        return res
