from odoo import models, fields, api
from datetime import date

class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection([
        ('cdi', 'CDI (Indéterminé)'),
        ('cdd', 'CDD (Déterminé)')
    ], string="Type de Contrat", default='cdi')
    trial_period_end = fields.Date(string="Fin de période d'essai")
    attachment = fields.One2many("ir.attachment", "res_id", string="Copie du contrat (PDF)")
    
