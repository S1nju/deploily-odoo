from odoo import models, fields


class HrEvaluationLine(models.Model):
    _name = 'hr.evaluation.line'
    _description = 'Lignes d Evaluation'

    evaluation_id = fields.Many2one('hr.evaluation', string="Référence Évaluation", ondelete='cascade')
    
    # Critères basés sur votre diagramme
    performance = fields.Selection([
        ('insuffisant', 'Insuffisant'),
        ('moyen', 'Moyen'),
        ('bien', 'Bien'),
        ('excellent', 'Excellent')
    ], string="Niveau de Performance", required=True)
    
    descipline = fields.Char(string="Critère / Observation")
