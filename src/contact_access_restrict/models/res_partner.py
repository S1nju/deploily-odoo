# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Technical field, not shown on any view. It lets the record rule in
    # security/contact_restrict_security.xml check whether the current
    # user is the Salesperson of ANY opportunity linked to this contact
    # (dot-notation traversal in ir.rule domains requires a real field).
    crm_lead_ids = fields.One2many(
        comodel_name='crm.lead',
        inverse_name='partner_id',
        string='Opportunities (technical)',
        help='Technical relation used by the "Contacts: restrict to own '
             'salesperson / creator" record rule. Do not remove.',
    )
