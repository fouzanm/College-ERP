from odoo import api, models


class CollegeMarksheetStudentwiseReport(models.AbstractModel):
    _name = 'report.college.report_marksheet_studentwise'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print(docids)
        docs = self.env['college.marksheet.wizard'].browse(docids)
        # print(docids)
        res = {
            'doc_ids': docids,
            'doc_model': 'college.marksheet.wizard',
            'docs': docs,
            'data': data,
        }
        print(res)
        return res
