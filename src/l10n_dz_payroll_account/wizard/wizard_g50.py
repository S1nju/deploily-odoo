# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class WizardG50(models.TransientModel):
    """
    Assistant de generation de la declaration G50.
    La G50 regroupe : IRG retenu + CNAS salariale + CNAS patronale
    pour une periode donnee.
    """
    _name = "l10n.dz.payroll.wizard.g50"
    _description = "Generation Declaration G50"

    date_from = fields.Date(
        string="Du",
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to = fields.Date(
        string="Au",
        required=True,
        default=fields.Date.today,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Societe",
        default=lambda self: self.env.company,
        required=True,
    )

    def action_print_g50(self):
        """Genere le rapport G50 pour la periode selectionnee."""
        self.ensure_one()
        slips = self.env["hr.payslip"].search([
            ("date_from", ">=", self.date_from),
            ("date_to", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
            ("state", "=", "done"),
        ])
        data = {
            "date_from": self.date_from,
            "date_to": self.date_to,
            "company_id": self.company_id.id,
            "slip_ids": slips.ids,
            "nombre_salaries": len(slips),
            "total_brut": sum(slips.mapped("montant_brut")),
            "total_cnas_sal": sum(slips.mapped("cotisation_cnas_salariale")),
            "total_cnas_pat": sum(slips.mapped("cotisation_cnas_patronale")),
            "total_cnas": (
                sum(slips.mapped("cotisation_cnas_salariale")) +
                sum(slips.mapped("cotisation_cnas_patronale"))
            ),
            "total_irg": sum(slips.mapped("montant_irg")),
            "total_net": sum(slips.mapped("net_a_payer")),
        }
        return self.env.ref(
            "l10n_dz_payroll_account.action_report_g50"
        ).report_action(self, data=data)
