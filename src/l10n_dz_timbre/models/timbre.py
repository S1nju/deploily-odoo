# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net
# Copyright (c) 2021 TransformaTek.dz  (<https://transformatek.dz/>)

from math import ceil
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ConfigTimbre(models.Model):
    _name = 'config.timbre'
    _description = 'Fiscal Timbre configuration'

    name = fields.Char('Nom', required=True)
    valeur = fields.Float('Valeur du timbre', digits='Product Price', required=True)
    tranche = fields.Float('Tranche', digits='Product Price', required=True)
    min_value = fields.Float('Valeur Minimum', digits='Product Price', required=True)
    max_value = fields.Float('Plafond', digits='Product Price', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'name must be unique per Company!'),
    ]

    @api.model
    def _timbre(self, montant, invoice_date=None):
        res = {}

        # Determine which logic to use based on invoice date
        # if invoice_date >= 01/01/2025 => new 2025 progressive logic
        # if invoice_date < 01/01/2025  => old logic
        date_2025 = date(2025, 1, 1)
        if invoice_date and invoice_date >= date_2025:
            # New 2025 progressive logic (Loi de Finances 2025)
            timbre = 0.0
            if montant > 300:
                if montant <= 30000:
                    timbre = ceil(montant / 100) * 1
                elif montant <= 100000:
                    timbre = ceil(montant / 100) * 1.5
                else:
                    timbre = ceil(montant / 100) * 2
                # Minimum 5 DA
                if timbre < 5:
                    timbre = 5
        else:
            # Old logic - use config.timbre parameters
            timbre_obj = self.env['config.timbre']
            liste_obj = timbre_obj.search([])
            if not liste_obj:
                raise UserError(_('Pas de confiuration du calcul Timbre.'))
            dict = liste_obj[-1]
            timbre = ceil((montant * dict['valeur']) / dict['tranche'])
            if timbre > dict['max_value']:
                timbre = dict['max_value']
            if timbre < dict['min_value']:
                timbre = dict['min_value']

        res['timbre'] = timbre
        res['amount_timbre'] = montant + timbre
        return res
