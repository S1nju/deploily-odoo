from odoo import models, fields


class HrEvaluation(models.Model):
    _name = 'hr.evaluation'
    _description = "Évaluation des employés"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employé",
        required=True
    )

    evaluation_date = fields.Date(
        string="Date d’évaluation",
        default=fields.Date.today
    )

    evaluator_id = fields.Many2one(
        'hr.employee',
        string="Évaluateur"
    )

    rating = fields.Selection([
        ('1', 'Médiocre'),
        ('2', 'En dessous de la moyenne'),
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent')
    ], string="Note globale")

    comments = fields.Text(
        string="Commentaires"
    )

    line_ids = fields.One2many(
        'hr.evaluation.line',
        'evaluation_id',
        string="Détails de l’évaluation"
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumise'),
        ('reviewed', 'Validée'),
        ('archived', 'Archivée')
    ], string="Statut", default='draft')

    def action_submit(self):
        for record in self:
            record.state = 'submitted'

    def action_review(self):
        for record in self:
            record.state = 'reviewed'
            
    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'


    def action_archive(self):
        for record in self:
            record.state = 'archived'