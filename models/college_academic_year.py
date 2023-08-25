# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CollegeAcademicYear(models.Model):
    """This is used to set academic year."""
    _name = "college.academic.year"
    _description = "Academic Year"

    name = fields.Char(compute="_compute_name", string="Academic Year",
                       store=True)
    academic_start = fields.Integer(string="Academic Start")
    academic_end = fields.Integer(string="Academic End")

    @api.depends('academic_start', 'academic_end')
    def _compute_name(self):
        """this method for concatenate academic start year and end year to find
        academic year"""
        for record in self:
            record.name = "{0}-{1}".format(str(record.academic_start),
                                           str(record.academic_end)[-2:])

    @api.constrains('academic_start', 'academic_end')
    def _validate_academic_year(self):
        """this will validate academic start year and end year for getting
         valid academic year."""
        if self.academic_end > self.academic_start:
            if len(str(self.academic_start)) != 4 \
                    and len(str(self.academic_end)) != 4:
                raise ValidationError("Invalid Academic Year Entry")
        else:
            raise ValidationError(
                "Academic Start Year must be less than Academic End Year.")
