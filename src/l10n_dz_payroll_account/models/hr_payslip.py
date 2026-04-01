# Part of OCA. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    """
    Extension comptable du bulletin de paie algérien.

    S'appuie sur payroll_account (OCA) pour la génération des écritures.
    Ajoute :
      - Journal de paie mensuel DZ
      - Ligne d'écriture pour CNAS patronale (charge hors bulletin salarié)
      - Export PC COMPTA / DFC
      - Avis de virement CCP CS 102
    """

    _inherit = "hr.payslip"

    # ── Champs supplémentaires ────────────────────────────────────────────────
    move_cnas_patronale_id = fields.Many2one(
        "account.move",
        string="Écriture CNAS Patronale",
        readonly=True,
        copy=False,
        help="Écriture comptable de la charge patronale CNAS (26%)",
    )

    # ── Surcharge de action_payslip_done ─────────────────────────────────────
    def action_payslip_done(self):
        """
        Appelle la logique OCA payroll_account puis génère en plus
        l'écriture de charge patronale CNAS algérienne.
        """
        res = super().action_payslip_done()
        for slip in self:
            slip._create_cnas_patronale_move()
        return res

    def action_payslip_cancel(self):
        """
        Annule l'écriture CNAS patronale en même temps que le bulletin.
        """
        for slip in self:
            if slip.move_cnas_patronale_id:
                if not slip.move_cnas_patronale_id.journal_id.restrict_mode_hash_table:
                    slip.move_cnas_patronale_id.with_context(
                        force_delete=True
                    ).button_cancel()
                    slip.move_cnas_patronale_id.with_context(
                        force_delete=True
                    ).unlink()
                else:
                    slip.move_cnas_patronale_id._reverse_moves()
                    slip.move_cnas_patronale_id = False
        return super().action_payslip_cancel()

    # ── Méthodes privées ──────────────────────────────────────────────────────

    def _create_cnas_patronale_move(self):
        """
        Crée l'écriture comptable de la charge patronale CNAS (26%).
        Cette charge n'est pas une retenue sur le bulletin salarié mais
        une charge supplémentaire de l'employeur.
        """
        self.ensure_one()
        cnas_pat_line = self.line_ids.filtered(
            lambda l: l.code == "CNAS_PAT"
        )
        if not cnas_pat_line or not self.journal_id:
            return

        amount = abs(cnas_pat_line.total)
        if not amount:
            return

        # Récupère les comptes débit/crédit de la règle CNAS_PAT
        rule = cnas_pat_line.salary_rule_id
        debit_account = rule.account_debit
        credit_account = rule.account_credit

        if not debit_account or not credit_account:
            _logger.warning(
                "CNAS Patronale: comptes comptables non configurés sur la "
                "règle %s. Écriture non générée.", rule.name
            )
            return

        date = self.date or self.date_to
        currency = self.company_id.currency_id

        move_vals = {
            "narration": _("Charge patronale CNAS - %s") % self.employee_id.name,
            "ref": self.number,
            "journal_id": self.journal_id.id,
            "date": date,
            "line_ids": [
                (0, 0, {
                    "name": _("CNAS Patronale 26% - %s") % self.employee_id.name,
                    "account_id": debit_account.id,
                    "debit": amount,
                    "credit": 0.0,
                    "date": date,
                }),
                (0, 0, {
                    "name": _("CNAS Patronale 26% - %s") % self.employee_id.name,
                    "account_id": credit_account.id,
                    "debit": 0.0,
                    "credit": amount,
                    "date": date,
                }),
            ],
        }
        move = self.env["account.move"].create(move_vals)
        move.action_post()
        self.move_cnas_patronale_id = move

    def _get_dz_journal_export_lines(self):
        """
        Retourne les lignes formatées pour l'export PC COMPTA / DFC.
        Format : N° compte | Libellé | Débit | Crédit | Date | Référence
        """
        self.ensure_one()
        lines = []
        if self.move_id:
            for ml in self.move_id.line_ids:
                lines.append({
                    "compte": ml.account_id.code,
                    "libelle": ml.name,
                    "debit": ml.debit,
                    "credit": ml.credit,
                    "date": ml.date,
                    "ref": self.number,
                    "matricule": self.contract_id.matricule or "",
                })
        if self.move_cnas_patronale_id:
            for ml in self.move_cnas_patronale_id.line_ids:
                lines.append({
                    "compte": ml.account_id.code,
                    "libelle": ml.name,
                    "debit": ml.debit,
                    "credit": ml.credit,
                    "date": ml.date,
                    "ref": self.number,
                    "matricule": self.contract_id.matricule or "",
                })
        return lines
