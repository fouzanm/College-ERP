# -*- coding: utf-8 -*-
from odoo import api, Command, fields, models
from odoo.exceptions import ValidationError


class CollegePromotion(models.Model):
    """this is used to promote class if student pass the exam."""
    _name = 'college.promotion'
    _description = 'Promotion Class'
    _rec_name = "class_id"

    exam_id = fields.Many2one('college.exam',)
    class_id = fields.Many2one('college.class', related="exam_id.class_id")
    semester_id = fields.Many2one('college.semester',
                                  related="exam_id.semester_id")
    promoted_students_ids = fields.One2many('college.marksheet',
                                            'promoted_students_id')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('pending', 'Pending'),
                                        ('completed', 'Completed')],
                             default='draft')

    def action_generate_students(self):
        """button action to generate qualified students"""
        marksheet = self.env['college.marksheet'].search([
            ('exam_id', '=', self.exam_id.id),
            ('exam_id.state', '=', 'completed'),
            ('result', '=', 'true')])
        for record in marksheet:
            self.write({'promoted_students_ids': [Command.link(record.id)]})
        self.state = 'pending'

    def action_promote_students(self):
        """button action to promote class of students."""
        self.state = 'completed'
        if self.class_id.promotion_id:
            students = self.env['college.students'].search([
                ('id', '=', self.promoted_students_ids.students_id.id)
            ])
            students.write({
                'class_id': self.class_id.promotion_id.id
            })

    @api.constrains('exam_id')
    def check_promotion_existence(self):
        """this function to block creating promotion class, if the promotion
        class already created."""
        existing_class = self.search([
            ('exam_id', '=', self.exam_id.id)
        ])
        if len(existing_class) > 1:
            raise ValidationError("Promotion Class already exist")
