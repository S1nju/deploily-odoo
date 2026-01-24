from odoo import models, fields, api


class HrContractArticle(models.Model):
    _name = 'hr.contract.article'
    _description = 'Contract Article'

    name = fields.Char(string='Title', required=True)
    content = fields.Text(string='Content')
    sequence = fields.Integer(string='Sequence', default=10)
    template_id = fields.Many2one('hr.contract.template', string='Template', ondelete='cascade')
    contract_id = fields.Many2one('hr.contract', string='Contract', ondelete='cascade')


class HrContractTemplate(models.Model):
    _name = 'hr.contract.template'
    _description = 'Contract Template'

    name = fields.Char(string='Template Name', required=True)
    note = fields.Text(string='Notes')
    article_ids = fields.One2many('hr.contract.article', 'template_id', string='Articles', copy=True)


