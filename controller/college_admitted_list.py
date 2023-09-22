# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CollegeAdmittedList(http.Controller):
    """to return online admission page"""
    @http.route(['/admission-list'], type='http', auth='public', website=True)
    def admitted_list(self):
        """function to show admitted list"""
        students = request.env["college.admission"].sudo().search([])
        user = request.env.user.active
        return request.render('college.admitted_list', {
            'students': students, 'user': user})

    @http.route("/admitted-list/confirm", type='json', auth='public')
    def action_confirm(self, record):
        """action to change state on confirm button"""
        (request.env['college.admission'].sudo().browse(record).
         action_admission_confirm())
