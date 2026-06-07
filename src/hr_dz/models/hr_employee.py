from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ss_number = fields.Char(
        string="N° de sécurité sociale",
        size=15
    )

    ccp_number = fields.Char(
        string="N° de compte CCP"
    )

    iep_rate = fields.Float(
        string="Taux IEP (%)",
        digits=(5, 2)
    )

    category = fields.Selection([
        ('cadre', 'Cadre'),
        ('maitrise', 'Maîtrise'),
        ('execution', 'Exécution')
    ], string="Catégorie professionnelle")

    commune_id = fields.Many2one(
        'res.country.state.commune',
        string='Commune',
        domain="[('state_id', '=', private_state_id)]",
    )
