# -*- coding: utf-8 -*-
from odoo import api, Command, fields, models
import datetime
from odoo.exceptions import ValidationError


class CollegeExam(models.Model):
    """This is used to add exam and its types.
    And also we can generate mark sheet in here."""
    _name = 'college.exam'
    _description = 'College Exam'

    name = fields.Char(compute="_compute_name", default="Exam Name")
    type = fields.Selection(selection=[('internal_exam', 'Internal Exam'),
                                       ('semester_exam', 'Semester Exam'),
                                       ('unit_test', 'Unit Test')],
                            required=True)
    class_id = fields.Many2one('college.class', 'Class',
                               required=True)
    course_id = fields.Many2one('college.course', 'Course',
                                related="class_id.course_id")
    semester_id = fields.Many2one('college.semester', 'Semester',
                                  related="class_id.semester_id")
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('completed', 'Completed')],
                             default='draft')
    papers_ids = fields.One2many("college.papers", "exam_id")
    students_count = fields.Integer(compute='_compute_students_count',
                                    store=True)
    marksheet_count = fields.Integer(compute='_compute_marksheet_count')

    @api.constrains('type', 'class_id')
    def _compute_name(self):
        """this function for exam naming."""
        for record in self:
            value = dict(record._fields['type'].selection).get(record.type)
            record.name = f"{value} {str(record.class_id.name)}"

    @api.onchange('type', 'class_id')
    def _onchange_type(self):
        """this function for setting subjects automatically,
        if exam type is semester exam."""
        self.update({
            'papers_ids': [(fields.Command.clear())]
        })
        if self.type == 'semester_exam':
            record_id = self.env['college.syllabus'].search([
                ('semester_id', '=', self.semester_id.id)])
            for record in record_id:
                self.write({'papers_ids': [Command.create({
                    'subject_id': record.id,
                    'max_mark': record.max_mark,
                    'pass_mark': record.pass_mark
                })]})

    @api.constrains('start_date', 'end_date')
    def _validate_exam_date(self):
        """this will validate exam start date and end date."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Invalid Exam Date Entry")

    def _end_date_status(self):
        """this for updating state to completed and generate marksheet if
         end date is over."""
        today = datetime.date.today()
        if self.start_date and self.end_date:
            if self.end_date < today:
                self.state = 'completed'
                self.generate_marksheet()

    def action_exam_confirm(self):
        """action for confirm button"""
        self.state = 'confirm'
        self._end_date_status()

    def action_exam_scheduler(self):
        """action to complete exam and generate marksheet on scheduled date"""
        exam = self.search([('state', '=', 'confirm')])
        for record in exam:
            record._end_date_status()

    @api.depends('class_id')
    def _compute_students_count(self):
        """used to calculate count of students who attended the exam."""
        for record in self:
            record.students_count = self.env['college.students'].search_count(
                [('class_id', '=', record.class_id.id)])

    @api.depends('end_date')
    def _compute_marksheet_count(self):
        """to compute generated marksheet count"""
        for record in self:
            record.marksheet_count = self.env['college.marksheet'].search_count(
                [('exam_id', '=', self.id)])

    def get_students(self):
        """action to view students"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'view_mode': 'tree',
            'res_model': 'college.students',
            'domain': [('class_id', '=', self.class_id.id)],
            'context': "{'create': False}"
        }

    def generate_marksheet(self):
        """action to generate mark sheet"""
        self.state = 'completed'
        self.ensure_one()
        for record in self.class_id.students_ids:
            marksheet = self.env['college.marksheet'].create({
                'students_id': record.id,
                'exam_id': self.id,
            })
            for rec in self.papers_ids:
                marksheet.write({
                    'papers_ids': [Command.create({
                        'subject_id': rec.subject_id.id,
                        'max_mark': rec.max_mark,
                        'pass_mark': rec.pass_mark
                    },
                    )]
                })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mark Sheet',
            'view_mode': 'tree,form',
            'res_model': 'college.marksheet',
            'domain': [('exam_id', '=', self.id)]
        }

    def get_marksheet(self):
        """action for smart button of generated mark sheet."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mark Sheet',
            'view_mode': 'tree,form',
            'res_model': 'college.marksheet',
            'domain': [('exam_id', '=', self.id)]
        }

    @api.constrains('type', 'class_id')
    def check_exam_existence(self):
        """this function to block creating exam, if that exam already created.
        """
        existing_exam = self.search([
            ('type', '=', self.type),
            ('class_id', '=', self.class_id.id)
        ])
        if len(existing_exam) > 1:
            raise ValidationError("Exam already exist")
