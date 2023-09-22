# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo import Command


class CollegeAdmission(models.Model):
    """This will collect all details of students during admission"""
    _name = "college.admission"
    _description = "College Admission"

    name = fields.Char(compute="_compute_name", string="Name")
    ad_no = fields.Char(string="Admission No:", readonly=True,
                        default=lambda self: _('New'), copy=False)
    ad_date = fields.Date(default=datetime.date.today(),
                          string="Admission Date")
    f_name = fields.Char(default="", required=True, string="First Name")
    l_name = fields.Char(default="", required=True, string="Last Name")
    father = fields.Char(string="Father's Name")
    mother = fields.Char(string="Mother's Name")
    communication_address = fields.Text(copy=False)
    permanent_address = fields.Text(copy=False)
    same_address = fields.Boolean(string="Same as Communication Address",
                                  copy=False)
    phone = fields.Char(string="Phone No")
    email = fields.Char(copy=False)
    course_id = fields.Many2one("college.course", "Course",
                                related="semester_id.course_id")
    semester_id = fields.Many2one("college.semester", "Semester",
                                  required=True)
    date_application = fields.Date(string="Date Of Application",
                                   default=datetime.date.today())
    academic_year_id = fields.Many2one("college.academic.year",
                                       required=True)
    prev_qualification = fields.Selection(string="Previous Qualification",
                                          selection=[('hs', 'Higher Secondary'),
                                                     ('ug', 'UG'),
                                                     ('pg', 'PG')])
    institute = fields.Char(string='Education Institution')
    tc = fields.Binary(string="Transfer Certificate")
    file_name = fields.Char()
    state = fields.Selection(default="draft",
                             selection=[('draft', 'Draft'),
                                        ('application', 'Application'),
                                        ('done', 'Done'),
                                        ('approved', 'Approved'),
                                        ('rejected', 'Rejected')])

    @api.depends('f_name', 'l_name')
    def _compute_name(self):
        """this function is used concatenate first name
         and last name to find full name."""
        for record in self:
            record.name = f'{str(record.f_name)} {str(record.l_name)}'

    def action_admission_confirm(self):
        """to change state of admission
        and if it is done state then automatically send email to student."""
        if self.state == 'application':
            self.state = 'done'
            CollegeAdmission.create_students_and_class(self)
            mail_template = self.env.ref(
                'college.college_admission_email_template')
            mail_template.send_mail(self.id, force_send=True)
        if self.state == 'draft':
            if self.tc:
                self.state = 'application'
            else:
                raise ValidationError("Add Attachment")

    @api.model
    def create(self, vals):
        """to create admission number"""
        if vals.get('ad_no', _('New')) == _('New'):
            vals['ad_no'] = self.env['ir.sequence'].next_by_code(
                'college.admission.number') or _('New')
        res = super(CollegeAdmission, self).create(vals)
        return res

    def action_admission_reject(self):
        """to send email if the student admission got rejected. """
        self.state = 'rejected'
        mail_template = self.env.ref(
            'college.college_admission_rejected_email_template')
        mail_template.send_mail(self.id, force_send=True)

    def create_students_and_class(self):
        """
        this function for push datas from admission record to students record.
        """
        students = self.env['college.students'].create({
            'name': self.name,
            'ad_no': self.ad_no,
            'ad_date': self.ad_date,
            'f_name': self.f_name,
            'l_name': self.l_name,
            'father': self.father,
            'mother': self.mother,
            'communication_address': self.communication_address,
            'permanent_address': self.permanent_address,
            'same_address': self.same_address,
            'phone': self.phone,
            'email': self.email,
            'course_id': self.course_id.id,
            'academic_year_id': self.academic_year_id.id,
            'semester_id': self.semester_id.id
        })
        if self.semester_id and self.academic_year_id:
            existing_class = self.env['college.class'].search([
                ('semester_id', '=', self.semester_id.id),
                ('academic_year_id', '=', self.academic_year_id.id)
            ], limit=1)
            if not existing_class:
                self.env['college.class'].create({
                    'semester_id': self.semester_id.id,
                    'academic_year_id': self.academic_year_id.id,
                    'course_id': self.course_id.id
                })
                student_id = self.env['college.students'].search(
                    [], order="id desc")[0]
                class_id = self.env['college.class'].search(
                    [], order="id desc")[0]
                student_id.write({
                    "class_id": class_id.id
                })
            else:
                existing_class.write({
                    'students_ids': [Command.link(students.id)]})
        return students
