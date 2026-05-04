# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CompteTresorerie(models.Model):
    _name = "compte.tresorerie"
    _description = "Compte de trésorerie"
    _order = "sequence asc, name asc"

    name = fields.Char(string="Nom du compte", required=True)
    sequence = fields.Integer(string="Ordre", default=10)
    active = fields.Boolean(default=True)

    solde_initial = fields.Monetary(
        string="Solde initial (ouverture)",
        currency_field='currency_id',
        default=0.0,
    )

    journal_id = fields.Many2one(
        'account.journal',
        string="Journal comptable",
        domain="[('type', 'in', ['bank', 'cash'])]",
    )
    type_journal = fields.Selection(
        related='journal_id.type',
        string="Type",
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True,
    )

    solde_reel = fields.Monetary(
        string="Solde réel (compta)",
        compute='_compute_solde_reel',
        currency_field='currency_id',
    )

    # KEY FIX: computed via SQL so it always reflects real flux data
    solde_previsionnel = fields.Monetary(
        string="Solde prévisionnel",
        compute='_compute_solde_previsionnel',
        currency_field='currency_id',
    )

    color = fields.Integer(string="Couleur", default=0)

    @api.depends('journal_id', 'company_id')
    def _compute_solde_reel(self):
        for compte in self:
            if not compte.journal_id:
                compte.solde_reel = 0.0
                continue
            self.env.cr.execute("""
                SELECT COALESCE(SUM(aml.debit - aml.credit), 0.0)
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN account_account aa ON aa.id = aml.account_id
                WHERE aml.journal_id = %s
                  AND am.state = 'posted'
                  AND aa.account_type IN ('asset_cash', 'asset_bank')
                  AND am.company_id = %s
            """, (compte.journal_id.id, compte.company_id.id))
            row = self.env.cr.fetchone()
            compte.solde_reel = row[0] if row else 0.0

    # No @api.depends on flux fields (computed fields can't depend on other
    # model's fields directly) — we use SQL and invalidate via flux write/create
    def _compute_solde_previsionnel(self):
        for compte in self:
            if not compte.id:
                compte.solde_previsionnel = compte.solde_initial
                continue
            self.env.cr.execute("""
                SELECT COALESCE(SUM(montant_entree - montant_sortie), 0.0)
                FROM flux_tresorerie
                WHERE compte_id = %s AND active = TRUE
            """, (compte.id,))
            row = self.env.cr.fetchone()
            flux_total = row[0] if row else 0.0
            compte.solde_previsionnel = compte.solde_initial + flux_total

    def action_voir_flux(self):
        return {
            'name': f"Flux – {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'flux.tresorerie',
            'view_mode': 'list,form,graph',
            'domain': [('compte_id', '=', self.id)],
            'context': {'default_compte_id': self.id},
        }

    def action_modifier_ouverture(self):
        """Open a small wizard to update solde_initial."""
        return {
            'name': f"Modifier le solde initial – {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'compte.tresorerie',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'form_view_ref': 'tresorerie_pro.view_compte_tresorerie_ouverture_form'},
        }
