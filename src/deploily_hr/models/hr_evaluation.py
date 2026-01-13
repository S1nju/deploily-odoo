from odoo import models, fields


class HrEvaluation(models.Model):
    _name = 'hr.evaluation'
    _description = 'Campagne d Evaluation'
    _rec_name = 'nom'
    evaluation_line_ids = fields.One2many(
        'hr.evaluation.line', 
        'evaluation_id', 
    
    )
    nom = fields.Char(string="Nom de la Campagne", required=True)
    date_compagne = fields.Date(string="Date de la Campagne", default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', string="Salarié évalué")
    evolution_type = fields.Selection([
        ('promotion', 'Promotion'),
        ('augmentation', 'Augmentation'),
        ('stagnation', 'Maintien au poste')
    ], string="Type d'évolution")
    
    # Relation vers les lignes de critères
    evaluation_line_ids = fields.One2many(
        'hr.evaluation.line', 
        'evaluation_id', 
        string="Détails de la Performance"
    )
