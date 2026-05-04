# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


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
        # Pass all data via context so the template can access it
        return {
            'type': 'ir.actions.report',
            'report_name': 'l10n_dz_payroll_account.report_g50_template',
            'report_type': 'qweb-pdf',
            'report_file': 'l10n_dz_payroll_account.report_g50_template',
            'name': 'Declaration G50',
            'context': {
                'discard_logo_check': True,
                'no_document_layout': True,
                'active_ids': self.ids,
                'active_model': 'l10n.dz.payroll.wizard.g50',
                'g50_date_from': str(self.date_from),
                'g50_date_to': str(self.date_to),
                'g50_company_id': self.company_id.id,
                'g50_company_name': self.company_id.name,
                'g50_company_vat': self.company_id.vat or '-',
                'g50_company_address': (self.company_id.street or '') + ' ' + (self.company_id.city or ''),
                'g50_nombre_salaries': len(slips),
                'g50_total_brut': sum(slips.mapped('montant_brut')),
                'g50_total_irg': sum(slips.mapped('montant_irg')),
                'g50_total_cnas_sal': sum(slips.mapped('cotisation_cnas_salariale')),
                'g50_total_cnas_pat': sum(slips.mapped('cotisation_cnas_patronale')),
                'g50_total_cnas': (
                    sum(slips.mapped('cotisation_cnas_salariale')) +
                    sum(slips.mapped('cotisation_cnas_patronale'))
                ),
                'g50_total_net': sum(slips.mapped('net_a_payer')),
                'g50_slip_ids': slips.ids,
            },
        }