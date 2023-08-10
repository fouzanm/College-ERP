# -*- coding: utf-8 -*-
from odoo import api, models


class CollegeMarksheetStudentwiseReport(models.AbstractModel):
    _name = 'report.college.report_marksheet_classwise'
    _description = "College Marksheet Studentwise report Model"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['college.marksheet.wizard'].browse(docids)
        res = {
            'doc_ids': docids,
            'doc_model': 'college.marksheet.wizard',
            'docs': docs,
            'data': data,
        }
        return res
