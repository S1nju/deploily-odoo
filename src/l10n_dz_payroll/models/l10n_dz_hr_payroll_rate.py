# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class L10nDzHrPayrollRate(models.Model):
    """
    Taux légaux de la paie algérienne.
    Centralize all legal rates: CNAS, IRG, IEP, SMIG, etc.
    """

    _name = "l10n.dz.hr.payroll.rate"
    _description = "Taux Légaux Paie Algérienne"
    _order = "date_from desc"

    name = fields.Char(string="Désignation", required=True)
    date_from = fields.Date(
        string="Date de début",
        required=True,
        default=fields.Date.today,
    )
    date_to = fields.Date(string="Date de fin")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Société",
        default=lambda self: self.env.company,
    )

    # ── SMIG ──────────────────────────────────────────────────────────────────
    smig = fields.Float(
        string="SMIG (DA)",
        default=20000.0,
        help="Salaire Minimum Interprofessionnel Garanti en Dinars Algériens",
    )

    # ── CNAS – Cotisations sociales ───────────────────────────────────────────
    cnas_salarial_rate = fields.Float(
        string="Taux CNAS Salarial (%)",
        default=9.0,
        help="Part salariale des cotisations CNAS (9%)",
    )
    cnas_patronal_rate = fields.Float(
        string="Taux CNAS Patronal (%)",
        default=26.0,
        help="Part patronale des cotisations CNAS (26%)",
    )
    cnas_plafond = fields.Float(
        string="Plafond CNAS (DA)",
        default=120000.0,
        help="Plafond mensuel de cotisation CNAS",
    )

    # ── IRG – Impôt sur le Revenu Global ──────────────────────────────────────
    irg_abattement_rate = fields.Float(
        string="Abattement IRG (%)",
        default=40.0,
        help="Taux d'abattement applicable au salaire brut avant calcul IRG (40%)",
    )
    irg_abattement_min = fields.Float(
        string="Abattement IRG Minimum (DA)",
        default=12000.0,
        help="Montant minimum d'abattement annuel IRG",
    )
    irg_abattement_max = fields.Float(
        string="Abattement IRG Maximum (DA)",
        default=18000.0,
        help="Montant maximum d'abattement annuel IRG",
    )
    irg_deduction_conjoint = fields.Float(
        string="Déduction Conjoint (DA/mois)",
        default=1000.0,
    )
    irg_deduction_enfant = fields.Float(
        string="Déduction par enfant (DA/mois)",
        default=600.0,
    )

    # ── IEP – Indemnité d'Expérience Professionnelle ──────────────────────────
    iep_rate_per_year = fields.Float(
        string="Taux IEP par année (%)",
        default=1.0,
        help="Pourcentage du salaire de base par année d'ancienneté (1%/an)",
    )
    iep_max_rate = fields.Float(
        string="Taux IEP Maximum (%)",
        default=25.0,
        help="Plafond du taux IEP (25% du salaire de base)",
    )

    # ── Indemnités forfaitaires ───────────────────────────────────────────────
    indemnite_transport = fields.Float(
        string="Indemnité Transport (DA/mois)",
        default=3000.0,
    )
    indemnite_panier = fields.Float(
        string="Indemnité Panier (DA/jour)",
        default=120.0,
    )

    # ── Allocations familiales ────────────────────────────────────────────────
    allocation_familiale_rate = fields.Float(
        string="Taux Allocations Familiales (%)",
        default=2.0,
        help="Pourcentage du SMIG par enfant à charge",
    )

    # ── IRG Barème (tranches) ─────────────────────────────────────────────────
    irg_bracket_ids = fields.One2many(
        "l10n.dz.hr.payroll.irg.bracket",
        "rate_id",
        string="Tranches IRG",
        copy=True,
    )

    @api.model
    def get_current_rates(self, company_id=None, date=None):
        """Return the active rate record for a given company and date."""
        domain = [("active", "=", True)]
        if company_id:
            domain += [
                "|",
                ("company_id", "=", company_id),
                ("company_id", "=", False),
            ]
        if date:
            domain += [
                ("date_from", "<=", date),
                "|",
                ("date_to", ">=", date),
                ("date_to", "=", False),
            ]
        return self.search(domain, order="date_from desc", limit=1)


class L10nDzHrPayrollIRGBracket(models.Model):
    """
    Tranches du barème progressif de l'IRG (Impôt sur le Revenu Global).
    """

    _name = "l10n.dz.hr.payroll.irg.bracket"
    _description = "Tranches IRG"
    _order = "min_amount"

    rate_id = fields.Many2one(
        "l10n.dz.hr.payroll.rate",
        string="Taux légaux",
        required=True,
        ondelete="cascade",
    )
    min_amount = fields.Float(string="Montant minimum (DA/an)", required=True)
    max_amount = fields.Float(
        string="Montant maximum (DA/an)",
        help="Laisser à 0 pour la dernière tranche (infini)",
    )
    rate = fields.Float(string="Taux (%)", required=True)
    description = fields.Char(string="Description")
