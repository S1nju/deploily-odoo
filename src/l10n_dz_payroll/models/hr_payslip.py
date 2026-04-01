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
        Calcule l'IRG selon le barème progressif algérien.
        1. Calcul abattement : 40% du brut, plafonné entre min et max annuels
        2. Revenu net imposable annuel = (brut - abattement - déductions) * 12
        3. Application du barème progressif
        4. Retour du montant mensuel
        """
        self.ensure_one()
        rates = self._get_dz_rates()
        if not rates:
            return 0.0

        employee = self.employee_id

        # 1. Abattement forfaitaire
        abattement_annuel = salaire_brut_imposable * 12 * rates.irg_abattement_rate / 100.0
        abattement_annuel = max(
            rates.irg_abattement_min,
            min(abattement_annuel, rates.irg_abattement_max),
        )

        # 2. Déductions pour charges de famille
        deduction_conjoint = (
            0.0
            if employee.conjoint_travaille or employee.situation_familiale == "celibataire"
            else rates.irg_deduction_conjoint * 12
        )
        deduction_enfants = employee.nombre_enfants * rates.irg_deduction_enfant * 12

        # 3. Revenu net imposable annuel
        revenu_annuel = (salaire_brut_imposable * 12) - abattement_annuel
        revenu_net_annuel = max(0.0, revenu_annuel - deduction_conjoint - deduction_enfants)

        # 4. Application barème progressif
        irg_annuel = self._apply_irg_bareme(revenu_net_annuel, rates)

        # 5. Retour mensuel
        return irg_annuel / 12.0

    def _apply_irg_bareme(self, revenu_annuel, rates):
        """
        Applique le barème progressif IRG sur le revenu annuel.
        Si des tranches sont configurées, les utilise. Sinon utilise le barème légal.
        """
        brackets = rates.irg_bracket_ids.sorted("min_amount")
        if brackets:
            irg = 0.0
            remaining = revenu_annuel
            for bracket in brackets:
                if remaining <= 0:
                    break
                lower = bracket.min_amount
                upper = bracket.max_amount if bracket.max_amount > 0 else float("inf")
                taxable_in_bracket = min(remaining, upper - lower)
                if taxable_in_bracket > 0 and revenu_annuel > lower:
                    taxable = min(revenu_annuel, upper) - lower
                    irg += max(0, taxable) * bracket.rate / 100.0
            return irg
        else:
            # Barème légal par défaut (2023 - Article 104 du Code des Impôts directs)
            return self._irg_bareme_legal_default(revenu_annuel)

    @staticmethod
    def _irg_bareme_legal_default(revenu_annuel):
        """
        Barème IRG légal algérien par défaut (tranches annuelles en DA).
        Source : Code des Impôts Directs et Taxes Assimilées - Art. 104
        """
        if revenu_annuel <= 120000:
            return 0.0
        elif revenu_annuel <= 360000:
            return (revenu_annuel - 120000) * 0.20
        elif revenu_annuel <= 1200000:
            return 48000 + (revenu_annuel - 360000) * 0.30
        elif revenu_annuel <= 3600000:
            return 300000 + (revenu_annuel - 1200000) * 0.33
        else:
            return 1092000 + (revenu_annuel - 3600000) * 0.35

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
            * self.employee_id.nombre_enfants
        )
