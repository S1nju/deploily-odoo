from odoo import models, fields


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    attachment_file = fields.Binary(string="Justificatif d'absence")