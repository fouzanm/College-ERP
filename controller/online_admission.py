# -*- coding: utf-8 -*-
import base64
import datetime
from odoo import http
from odoo.http import request


class OnlineAdmission(http.Controller):
    """to return online admission page"""
    @http.route(['/admission'], type='http', auth='public', website=True)
    def online_admission(self):
        """function for online admission"""
        semester = request.env["college.semester"].sudo().search([])
        academic_year = request.env["college.academic.year"].sudo().search([])
        values = {
            'semester': semester,
            'academic_year': academic_year,
            'date': datetime.date.today()
        }
        user = request.env.user.partner_id
        if request.env.user.active:
            values.update({
                'f_name': user.name.split()[0],
                'l_name': " ".join(user.name.split()[1:]),
                'email': user.email,
                'phone': user.phone
            })
        return request.render('college.online_admission_form', values)

    @http.route('/admission/submit', type='http', auth='public', website=True)
    def create_admission(self, **post):
        """function to create admission"""
        if post.get('tc'):
            file_data = post.get('tc').read()
            file_name = post.get('tc').filename
            request.env['college.admission'].sudo().create({
                'f_name': post.get('f_name'),
                'l_name': post.get('l_name'),
                'phone': post.get('phone'),
                'email': post.get('email'),
                'ad_date': post.get('ad_date'),
                'semester_id': post.get('semester_id'),
                'academic_year_id': post.get('academic_year_id'),
                'tc': base64.b64encode(file_data),
                'file_name': file_name,
                'state': 'application'
            })
            return request.render('college.admission_success')
