from odoo import models, fields


class HrMessionScale(models.Model):
    _name = 'hr.mession.scale'
    _description = 'Barème des Missions'

    name = fields.Char(string="Désignation", required=True)
    mission_type = fields.Selection([
        ('national', 'National'),
        ('international', 'Étranger')
    ], string="Type de Mission")
    daily_amount = fields.Float(string="Indemnité Journalière (DZD/Devise)")
    is_covered = fields.Boolean(string="Prise en charge totale", default=False)
