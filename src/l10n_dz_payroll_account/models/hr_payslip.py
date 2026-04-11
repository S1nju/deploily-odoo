# Part of OCA. See LICENSE file for full copyright and licensing details.

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    """
    Extension comptable du bulletin de paie algerien.
    - Ecriture CNAS Patronale separee
    - Integration complete avec Invoicing (account.move)
    - Support export G50
    - Fiche de Paie + Grand Livre de Paie Global
    """
    _inherit = "hr.payslip"

    move_cnas_patronale_id = fields.Many2one(
        "account.move",
        string="Ecriture CNAS Patronale",
        readonly=True,
        copy=False,
    )

    # ── Confirmation bulletin ─────────────────────────────────────────────────
    def action_payslip_done(self):
        res = super().action_payslip_done()
        for slip in self:
            slip._create_cnas_patronale_move()
        return res

    # ── Annulation bulletin ───────────────────────────────────────────────────
    def action_payslip_cancel(self):
        for slip in self:
            if slip.move_cnas_patronale_id:
                move = slip.move_cnas_patronale_id
                if not move.journal_id.restrict_mode_hash_table:
                    move.with_context(force_delete=True).button_cancel()
                    move.with_context(force_delete=True).unlink()
                else:
                    move._reverse_moves()
                slip.move_cnas_patronale_id = False
        return super().action_payslip_cancel()

    # ── Ecriture CNAS Patronale ───────────────────────────────────────────────
    def _create_cnas_patronale_move(self):
        """
        Cree l'ecriture comptable de la charge patronale CNAS (26%).
        Debit  631000 Remunerations du personnel
        Credit 431000 CNAS a payer
        """
        self.ensure_one()
        cnas_pat_line = self.line_ids.filtered(lambda l: l.code == "CNAS_PAT")
        if not cnas_pat_line or not self.journal_id:
            return

        amount = abs(cnas_pat_line.total)
        if not amount:
            return

        rule = cnas_pat_line.salary_rule_id
        debit_account = rule.account_debit
        credit_account = rule.account_credit

        if not debit_account or not credit_account:
            _logger.warning(
                "CNAS Patronale: comptes non configures sur la regle %s", rule.name
            )
            return

        date = self.date or self.date_to
        move = self.env["account.move"].create({
            "narration": _("Charge patronale CNAS - %s") % self.employee_id.name,
            "ref": self.number,
            "journal_id": self.journal_id.id,
            "date": date,
            "line_ids": [
                (0, 0, {
                    "name": _("CNAS Patronale 26%% - %s") % self.employee_id.name,
                    "account_id": debit_account.id,
                    "debit": amount,
                    "credit": 0.0,
                    "date": date,
                }),
                (0, 0, {
                    "name": _("CNAS Patronale 26%% - %s") % self.employee_id.name,
                    "account_id": credit_account.id,
                    "debit": 0.0,
                    "credit": amount,
                    "date": date,
                }),
            ],
        })
        move.action_post()
        self.move_cnas_patronale_id = move

    # ── Donnees pour G50 ─────────────────────────────────────────────────────
    def get_g50_data(self):
        """
        Retourne les donnees necessaires pour la declaration G50.
        """
        self.ensure_one()
        return {
            "brut": self.montant_brut,
            "cnas_sal": self.cotisation_cnas_salariale,
            "cnas_pat": self.cotisation_cnas_patronale,
            "irg": self.montant_irg,
            "net": self.net_a_payer,
            "employee": self.employee_id.name,
            "matricule": self.contract_id.matricule or "",
            "periode": "%s/%s" % (self.date_from.month, self.date_from.year),
        }

    # ── Export PC COMPTA / DFC ────────────────────────────────────────────────
    def _get_dz_journal_export_lines(self):
        self.ensure_one()
        lines = []
        matricule = self.contract_id.matricule or ""
        ref = self.number or ""

        def _extract(move):
            for ml in move.line_ids:
                lines.append({
                    "compte": ml.account_id.code,
                    "libelle": ml.name,
                    "debit": ml.debit,
                    "credit": ml.credit,
                    "date": ml.date,
                    "ref": ref,
                    "matricule": matricule,
                })

        if self.move_id:
            _extract(self.move_id)
        if self.move_cnas_patronale_id:
            _extract(self.move_cnas_patronale_id)
        return lines


class HrPayslipRun(models.Model):
    """
    Extension du lot de bulletins pour la declaration G50.
    """
    _inherit = "hr.payslip.run"

    def get_g50_summary(self):
        """
        Retourne le resume G50 pour le lot de bulletins.
        Utilise dans le rapport G50.
        """
        self.ensure_one()
        slips = self.slip_ids.filtered(lambda s: s.state == "done")
        return {
            "periode": "%s/%s" % (self.date_start.month, self.date_start.year),
            "nombre_salaries": len(slips),
            "total_brut": sum(slips.mapped("montant_brut")),
            "total_cnas_sal": sum(slips.mapped("cotisation_cnas_salariale")),
            "total_cnas_pat": sum(slips.mapped("cotisation_cnas_patronale")),
            "total_cnas": sum(slips.mapped("cotisation_cnas_salariale")) +
                          sum(slips.mapped("cotisation_cnas_patronale")),
            "total_irg": sum(slips.mapped("montant_irg")),
            "total_net": sum(slips.mapped("net_a_payer")),
            "company": self.env.company,
        }
