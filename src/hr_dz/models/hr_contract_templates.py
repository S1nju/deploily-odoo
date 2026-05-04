from odoo import models, fields


class HrContractArticle(models.Model):
    _name = 'hr.contract.article'
    _description = 'Article de contrat'
    _order = 'sequence, id'

    name = fields.Char(
        string="Titre",
        required=True
    )

    content = fields.Text(
        string="Contenu"
    )

    sequence = fields.Integer(
        string="Séquence",
        default=10
    )

    template_id = fields.Many2one(
        'hr.contract.template',
        string="Modèle de contrat",
        ondelete='cascade'
    )

    contract_id = fields.Many2one(
        'hr.contract',
        string="Contrat",
        ondelete='cascade'
    )
class HrContractTemplate(models.Model):
    _name = 'hr.contract.template'
    _description = 'Modèle de contrat'

    name = fields.Char(
        string="Nom du modèle",
        required=True
    )

    note = fields.Text(
        string="Notes"
    )

    article_ids = fields.One2many(
        'hr.contract.article',
        'template_id',
        string="Articles",
        copy=True
    )