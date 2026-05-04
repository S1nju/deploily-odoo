# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net
# Copyright (c) 2021 TransformaTek.dz  (<https://transformatek.dz/>)

from math import ceil
from odoo import fields, models, api


class AccountInvoiceTimbre(models.Model):
    _inherit = 'account.move'

    is_cash_payment = fields.Boolean(
        string='Paiement en espèces',
        default=False,
        help='Activer si le paiement est en espèces. Le timbre sera affiché sur la facture PDF.'
    )
    amount_timbre = fields.Monetary(
        string='Timbre',
        readonly=True,
        compute='_compute_amount_timbre',
    )
    amount_total_timbre = fields.Monetary(
        string='Total avec Timbre',
        readonly=True,
        compute='_compute_amount_timbre',
    )

    @api.depends('amount_total', 'invoice_date', 'is_cash_payment')
    def _compute_amount_timbre(self):
        for order in self:
            if order.is_cash_payment:
                invoice_date = order.invoice_date
                timbre = self.env['config.timbre']._timbre(order.amount_total, invoice_date)
                order.amount_timbre = timbre['timbre']
                order.amount_total_timbre = timbre['amount_timbre']
            else:
                order.amount_timbre = 0.0
                order.amount_total_timbre = order.amount_total
