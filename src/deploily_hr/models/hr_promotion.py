from odoo import models, fields, api

class HrPromotion(models.Model):
    _name = 'hr.promotion'
    _description = 'Suivi de Carrière'

    employee_id = fields.Many2one('hr.employee', string="Employé")
    old_job_id = fields.Many2one('hr.job', string="Ancien Poste", related='employee_id.job_id', readonly=True, store=True)
    new_job_id = fields.Many2one('hr.job', string="Nouveau Poste")
    date_effective = fields.Date(string="Date de prise d'effet")
    type_promotion = fields.Selection([
        ('vertical', 'Promotion Verticale'),
        ('horizontal', 'Changement de poste')
    ], string="Type d'évolution")