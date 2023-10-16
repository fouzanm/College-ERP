# -*- coding: utf-8 -*-
from odoo import api, models


class CollegeMarksheetStudentwiseReport(models.AbstractModel):
    _name = 'report.college.report_marksheet_studentwise'
    _description = "College Marksheet Classwise report Model"

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'college.marksheet.wizard',
            'docs': self.env['college.marksheet.wizard'].browse(docids),
            'data': data,
        }
