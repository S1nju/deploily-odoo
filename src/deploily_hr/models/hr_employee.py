from odoo import models, fields, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ss_number = fields.Char(string="N° Sécurité Sociale", size=15)
    ccp_number = fields.Char(string="N° de compte CCP")
    iep_rate = fields.Float(string="Taux IEP (%)", compute="_compute_iep", store=True)
    category = fields.Selection([
        ('cadre', 'Cadre'),
        ('maitrise', 'Maîtrise'),
        ('execution', 'Exécution')
    ], string="Catégorie Professionnelle")

 

