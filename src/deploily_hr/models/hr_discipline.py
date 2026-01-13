from odoo import models, fields


class HrDiscipline(models.Model):
    _name = 'hr.discipline'
    _description = 'Dossier Disciplinaire'

    employee_id = fields.Many2one('hr.employee', string="Salarié")
    type_sanction = fields.Selection([
        ('avertissement', 'Avertissement'),
        ('blame', 'Blâme'),
        ('mise_a_pied', 'Mise à pied'),
        ('licenciement', 'Licenciement')
    ], string="Type de Sanction")
    date_incident = fields.Date(string="Date de l'incident")
    document_joint = fields.One2many(
        'ir.attachment',
        'res_id',
        string="Documents joints",
        
    )

