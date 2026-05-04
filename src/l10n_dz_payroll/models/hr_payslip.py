# Part of OCA. See LICENSE file for full copyright and licensing details.

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrPayslip(models.Model):
    """
    Extension du bulletin de paie pour la réglementation algérienne.
    Fournit des méthodes de calcul CNAS, IRG, IEP accessibles depuis
    les règles salariales via l'objet `payslip`.
    """

    _inherit = "hr.payslip"

    # ── Champs algériens ──────────────────────────────────────────────────────
    type_bulletin = fields.Selection(
        [
            ("salaire", "Salaire"),
            ("rappel", "Rappel"),
            ("prime", "Prime (PRI-PRC)"),
        ],
        string="Type de bulletin",
        default="salaire",
    )
    moyen_paiement = fields.Selection(
        [
            ("virement", "Virement bancaire"),
            ("ccp", "Virement CCP"),
            ("especes", "Espèces"),
            ("cheque", "Chèque"),
        ],
        string="Moyen de paiement",
        default="virement",
    )
    # Résultats calculés stockés pour reporting
    montant_brut = fields.Monetary(
        string="Salaire Brut",
        currency_field="currency_id",
        compute="_compute_algerian_totals",
        store=True,
    )
    cotisation_cnas_salariale = fields.Monetary(
        string="CNAS Salariale",
        currency_field="currency_id",
        compute="_compute_algerian_totals",
        store=True,
    )
    cotisation_cnas_patronale = fields.Monetary(
        string="CNAS Patronale",
        currency_field="currency_id",
        compute="_compute_algerian_totals",
        store=True,
    )
    montant_irg = fields.Monetary(
        string="IRG",
        currency_field="currency_id",
        compute="_compute_algerian_totals",
        store=True,
    )
    net_a_payer = fields.Monetary(
        string="Net à Payer",
        currency_field="currency_id",
        compute="_compute_algerian_totals",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )

    @api.depends("line_ids", "line_ids.total")
    def _compute_algerian_totals(self):
        for slip in self:
            slip.montant_brut = slip.get_salary_line_total("BRUT")
            slip.cotisation_cnas_salariale = abs(
                slip.get_salary_line_total("CNAS_SAL")
            )
            slip.cotisation_cnas_patronale = abs(
                slip.get_salary_line_total("CNAS_PAT")
            )
            slip.montant_irg = abs(slip.get_salary_line_total("IRG"))
            slip.net_a_payer = slip.get_salary_line_total("NET")

    # ── Méthodes utilitaires accessibles dans les règles salariales ───────────

    def _get_dz_rates(self):
        """Return current Algerian legal rates record."""
        self.ensure_one()
        Rate = self.env["l10n.dz.hr.payroll.rate"]
        return Rate.get_current_rates(
            company_id=self.company_id.id,
            date=self.date_to,
        )

    def compute_anciennete(self):
        """
        Calcule le nombre d'années d'ancienneté à la date de fin de bulletin.
        Utilise contract.date_recrutement ou contract.date_start.
        """
        self.ensure_one()
        contract = self.contract_id
        date_recrutement = (
            contract.date_recrutement or contract.date_start
        )
        if not date_recrutement:
            return 0
        delta = relativedelta(self.date_to, date_recrutement)
        return delta.years

    def compute_iep(self, salaire_base):
        """
        Calcule l'Indemnité d'Expérience Professionnelle (IEP).
        IEP = salaire_base * min(ancienneté * taux_par_an, taux_max)
        """
        self.ensure_one()
        rates = self._get_dz_rates()
        if not rates:
            return 0.0
        anciennete = self.compute_anciennete()
        taux = min(
            anciennete * rates.iep_rate_per_year,
            rates.iep_max_rate,
        )
        return salaire_base * taux / 100.0

    def compute_cnas_salariale(self, salaire_brut_cotisable):
        """
        Calcule la cotisation CNAS salariale.
        Base = min(brut cotisable, plafond CNAS)
        """
        self.ensure_one()
        rates = self._get_dz_rates()
        if not rates:
            return 0.0
        base = min(salaire_brut_cotisable, rates.cnas_plafond)
        return base * rates.cnas_salarial_rate / 100.0

    def compute_cnas_patronale(self, salaire_brut_cotisable):
        """
        Calcule la cotisation CNAS patronale.
        Base = min(brut cotisable, plafond CNAS)
        """
        self.ensure_one()
        rates = self._get_dz_rates()
        if not rates:
            return 0.0
        base = min(salaire_brut_cotisable, rates.cnas_plafond)
        return base * rates.cnas_patronal_rate / 100.0

    def compute_irg(self, salaire_brut_imposable):
        """
        Calcule l'IRG mensuel algérien.
        Base = Brut imposable - Abattement 40% (min/max mensuels)
        Application directe du barème mensuel.
        """
        self.ensure_one()
        rates = self._get_dz_rates()
        if not rates:
            return 0.0

        employee = self.employee_id

        # 1. Abattement mensuel 40%
        abattement = salaire_brut_imposable * rates.irg_abattement_rate / 100.0
        abattement = max(
            rates.irg_abattement_min,
            min(abattement, rates.irg_abattement_max),
        )

        # 2. Déductions famille mensuelles
        deduction_conjoint = (
            0.0
            if employee.conjoint_travaille or employee.situation_familiale == "celibataire"
            else rates.irg_deduction_conjoint
        )
        deduction_enfants = employee.nb_enfants_dz * rates.irg_deduction_enfant

        # 3. Revenu net imposable mensuel
        revenu_net = max(0.0, salaire_brut_imposable - abattement - deduction_conjoint - deduction_enfants)

        # 4. Application barème progressif mensuel - pas de division par 12
        return self._apply_irg_bareme(revenu_net, rates)

    def _apply_irg_bareme(self, revenu_mensuel, rates):
        """
        Applique le barème progressif IRG mensuel tranche par tranche.
        """
        brackets = rates.irg_bracket_ids.sorted("min_amount")
        if not brackets:
            return self._irg_bareme_legal_default(revenu_mensuel)

        irg = 0.0
        for bracket in brackets:
            lower = bracket.min_amount
            upper = bracket.max_amount if bracket.max_amount > 0 else float("inf")
            if revenu_mensuel <= lower:
                break
            taxable = min(revenu_mensuel, upper) - lower
            if taxable > 0:
                irg += taxable * bracket.rate / 100.0
        return irg

    @staticmethod
    def _irg_bareme_legal_default(revenu_mensuel):
        """
        Barème IRG mensuel légal algérien par défaut.
        """
        if revenu_mensuel <= 20000:
            return 0.0
        elif revenu_mensuel <= 40000:
            return (revenu_mensuel - 20000) * 0.20
        elif revenu_mensuel <= 80000:
            return 4000 + (revenu_mensuel - 40000) * 0.25
        else:
            return 14000 + (revenu_mensuel - 80000) * 0.30
        
    def compute_allocations_familiales(self):
            """
            Calcule les allocations familiales.
            Base = SMIG * taux * nombre d'enfants
            """
            self.ensure_one()
            rates = self._get_dz_rates()
            if not rates:
                return 0.0
            return (
                rates.smig
                * rates.allocation_familiale_rate
                / 100.0
                * self.employee_id.nb_enfants_dz
            )