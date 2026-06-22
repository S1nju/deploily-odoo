# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net

from odoo import fields, models


class ResCountryStateCommune(models.Model):
    _name = 'res.country.state.commune'
    _description = 'Commune'
    _order = 'name'

    name = fields.Char(string='Commune', required=True)
    code = fields.Char(string='Code', required=True)
    state_id = fields.Many2one('res.country.state', string='Wilaya', required=True)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rc = fields.Char(string='R.C')
    nif = fields.Char(string='N.I.F', size=15)
    nis = fields.Char(string='N.I.S')
    ai = fields.Char(string='Article d\'imposition')
    commune_id = fields.Many2one(
        'res.country.state.commune',
        string='Commune',
        domain="[('state_id', '=', state_id)]",
    )


# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     rc = fields.Char(string='R.C')
#     nif = fields.Char(string='N.I.F', size=15)
#     nis = fields.Char(string='N.I.S')
#     ai = fields.Char(string='Article d\'imposition')
#     commune_id = fields.Many2one(
#         'res.country.state.commune',
#         string='Commune',
#         domain="[('state_id', '=', state_id)]",
#     )


