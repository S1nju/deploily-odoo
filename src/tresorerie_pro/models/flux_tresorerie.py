# -*- coding: utf-8 -*-
import logging
from datetime import timedelta, datetime
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FluxTresorerie(models.Model):
    _name = "flux.tresorerie"
    _description = "Flux de trésorerie"
    _order = "date asc, id asc"

    name = fields.Char(
        string="Référence",
        readonly=True, required=True, copy=False,
        default="Nouveau",
    )
    compte_id = fields.Many2one(
        'compte.tresorerie', string="Compte",
        required=True, ondelete='cascade', index=True,
    )
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True,
    )
    partner_id = fields.Many2one('res.partner', string="Partenaire")

    date = fields.Datetime(string="Date", index=True)
    date_prevue = fields.Datetime(
        string="Date prévue",
        default=lambda self: datetime.now(),
        index=True,
    )
    date_effective = fields.Datetime(string="Date effective")

    montant_entree = fields.Monetary(string="Entrée (+)", currency_field='currency_id')
    montant_sortie = fields.Monetary(string="Sortie (-)", currency_field='currency_id')
    balance = fields.Monetary(
        string="Balance", compute='_compute_balance',
        currency_field='currency_id', store=True,
    )

    solde_precedent = fields.Monetary(
        string="Solde n-1", compute='_compute_soldes_cumules',
        currency_field='currency_id',
    )
    solde_courant = fields.Monetary(
        string="Solde", compute='_compute_soldes_cumules',
        currency_field='currency_id',
    )

    state = fields.Selection(
        [('prevu', 'Prévu'), ('en_cours', 'En cours'), ('fait', 'Fait')],
        string="État", default='prevu', index=True,
    )
    lock_status = fields.Char(string=" ", compute='_compute_lock_status')

    label = fields.Char(string="Désignation")
    active = fields.Boolean(default=True)
    seq_arch = fields.Integer(default=10)

    type_recurrence = fields.Selection(
        [('once', 'Une seule fois'), ('jour', 'Chaque jour'),
         ('semaine', 'Chaque semaine'), ('mois', 'Chaque mois')],
        string="Fréquence", default='once',
    )
    date_debut = fields.Datetime(string="Date de début")
    date_fin = fields.Datetime(string="Date de fin")

    # ── Computes ──────────────────────────────────────────────────────────────

    @api.depends('state')
    def _compute_lock_status(self):
        m = {'prevu': '', 'en_cours': '⬅️', 'fait': '✅'}
        for rec in self:
            rec.lock_status = m.get(rec.state, '')

    @api.depends('montant_entree', 'montant_sortie')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.montant_entree - rec.montant_sortie

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        def _to_tuple(t):
            return tuple(map(_to_tuple, t)) if isinstance(t, (list, tuple)) else t
        order = order or self._order
        ctx = {'domain_cumul': _to_tuple(domain or []), 'order_cumul': order}
        return super(FluxTresorerie, self.with_context(**ctx)).search_read(
            domain, fields, offset, limit, order,
        )

    @api.depends_context('order_cumul', 'domain_cumul')
    def _compute_soldes_cumules(self):
        if not self.env.context.get('order_cumul'):
            # Form view fallback — no JOIN, separate queries to avoid GROUP BY issue
            for rec in self:
                if not rec.id or not rec.compte_id:
                    rec.solde_courant = 0.0
                    rec.solde_precedent = 0.0
                    continue

                self.env.cr.execute(
                    "SELECT COALESCE(solde_initial, 0.0) FROM compte_tresorerie WHERE id = %s",
                    (rec.compte_id.id,)
                )
                row = self.env.cr.fetchone()
                solde_initial = row[0] if row else 0.0

                self.env.cr.execute("""
                    SELECT COALESCE(SUM(montant_entree - montant_sortie), 0.0)
                    FROM flux_tresorerie
                    WHERE compte_id = %s AND active = TRUE
                      AND (date < %s OR (date = %s AND id <= %s))
                """, (rec.compte_id.id, rec.date, rec.date, rec.id))
                row = self.env.cr.fetchone()
                rec.solde_courant = solde_initial + (row[0] if row and row[0] is not None else 0.0)

                self.env.cr.execute("""
                    SELECT COALESCE(SUM(montant_entree - montant_sortie), 0.0)
                    FROM flux_tresorerie
                    WHERE compte_id = %s AND active = TRUE
                      AND (date < %s OR (date = %s AND id < %s))
                """, (rec.compte_id.id, rec.date, rec.date, rec.id))
                row = self.env.cr.fetchone()
                rec.solde_precedent = solde_initial + (row[0] if row and row[0] is not None else 0.0)
            return

        order_str = self.env.context['order_cumul']
        domain = list(self.env.context.get('domain_cumul') or [])
        query = self._where_calc(domain)
        order_clause = ', '.join(
            self._generate_order_by_inner(self._table, order_str, query, reverse_direction=False)
        )
        from_clause, where_clause, where_params = query.get_sql()

        # FIX: use correlated subquery for solde_initial — no JOIN so no GROUP BY conflict
        sql = f"""
            WITH base AS (
                SELECT
                    ft.id,
                    ft.compte_id,
                    (SELECT COALESCE(ct.solde_initial, 0.0)
                     FROM compte_tresorerie ct WHERE ct.id = ft.compte_id) AS solde_initial,
                    SUM(ft.montant_entree - ft.montant_sortie) OVER (
                        PARTITION BY ft.compte_id
                        ORDER BY {order_clause}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS cumul_courant,
                    COALESCE(SUM(ft.montant_entree - ft.montant_sortie) OVER (
                        PARTITION BY ft.compte_id
                        ORDER BY {order_clause}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ), 0) AS cumul_precedent
                FROM {from_clause} AS ft
                WHERE {where_clause or 'TRUE'}
            )
            SELECT id,
                   solde_initial + cumul_courant   AS solde_courant,
                   solde_initial + cumul_precedent AS solde_precedent
            FROM base
        """
        self.env.cr.execute(sql, where_params)
        result = {row[0]: (row[1] or 0.0, row[2] or 0.0) for row in self.env.cr.fetchall()}
        for record in self:
            cumul, cumul_prec = result.get(record.id, (0.0, 0.0))
            record.solde_courant = cumul
            record.solde_precedent = cumul_prec

    # ── ORM — invalidate compte cache after every flux change ─────────────────

    def _invalidate_compte_cache(self, compte_ids):
        if compte_ids:
            self.env['compte.tresorerie'].browse(list(set(compte_ids))).invalidate_recordset(
                ['solde_previsionnel']
            )

    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('flux.tresorerie') or 'Nouveau'
            if vals.get('state', 'prevu') != 'fait':
                vals['date'] = vals.get('date_prevue') or vals.get('date')
        records = super().create(vals_list)
        self._invalidate_compte_cache(records.mapped('compte_id').ids)
        return records

    def write(self, vals):
        for rec in self:
            if rec.state == 'fait' and any(
                k not in ('state', 'date_effective', 'lock_status') for k in vals
            ):
                raise UserError("Impossible de modifier un flux verrouillé (état : Fait).")
        result = super().write(vals)
        self._invalidate_compte_cache(self.mapped('compte_id').ids)
        return result

    def unlink(self):
        compte_ids = self.mapped('compte_id').ids
        for rec in self:
            if rec.state == 'fait':
                raise UserError("Impossible de supprimer un flux verrouillé (état : Fait).")
        result = super().unlink()
        self._invalidate_compte_cache(compte_ids)
        return result

    def toggle_active(self):
        archived = self.env['flux.tresorerie'].search_count([('active', '=', False)])
        k = archived + 1
        for rec in self:
            rec.seq_arch += k
            k += 1
        result = super().toggle_active()
        self._invalidate_compte_cache(self.mapped('compte_id').ids)
        return result

    # ── Workflow ──────────────────────────────────────────────────────────────

    def action_verrouiller(self):
        for rec in self:
            if rec.state == 'fait':
                raise UserError("Ce flux est déjà verrouillé.")
            rec.date_effective = rec.date_effective or rec.date
            rec.state = 'fait'
            next_flux = self.env['flux.tresorerie'].search(
                [('date', '>', rec.date), ('compte_id', '=', rec.compte_id.id)],
                order='date asc', limit=1,
            )
            if next_flux and next_flux.state == 'prevu':
                next_flux.state = 'en_cours'

    def action_deverrouiller(self):
        for rec in self:
            if rec.state != 'fait':
                raise UserError("Seuls les flux verrouillés peuvent être déverrouillés.")
            rec.state = 'en_cours'

    def action_detail(self):
        return {
            'name': "Détail du flux",
            'view_mode': 'form',
            'res_model': 'flux.tresorerie',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.onchange('date_prevue', 'state')
    def _onchange_date_prevue(self):
        if self.state in ('en_cours', 'prevu'):
            self.date = self.date_prevue

    @api.model
    def archiver_flux_expires(self):
        self = self.sudo()
        from odoo import fields as f
        today = f.Date.today()
        archived = self.env['flux.tresorerie'].search_count([('active', '=', False)])
        k = archived + 1
        for flux in self.env['flux.tresorerie'].search([('date_effective', '!=', False)]):
            if (flux.date_effective.date() + timedelta(days=30)) == today:
                flux.seq_arch += k
                flux.active = False
                k += 1
