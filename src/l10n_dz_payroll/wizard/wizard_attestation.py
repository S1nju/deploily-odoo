# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WizardAttestationTravail(models.TransientModel):
    _name = "wizard.attestation.travail"
    _description = "Attestation de Travail et de Salaire"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employe",
        required=True,
    )
    annee = fields.Integer(
        string="Annee",
        required=True,
        default=lambda self: fields.Date.today().year,
    )

    def action_print(self):
        self.ensure_one()
        report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'l10n_dz_payroll.report_attestation_travail_document')
        ], limit=1)
        return report.report_action(self, config=False)
