# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    @api.model
    def _default_journal_id(self):
        """Returns the DZ Paie journal as default for all new contracts."""
        journal = self.env["account.journal"].search([
            ("code", "=", "PAIE"),
            ("company_id", "=", self.env.company.id),
        ], limit=1)
        if not journal:
            journal = self.env["account.journal"].search([
                ("type", "=", "general"),
                ("company_id", "=", self.env.company.id),
            ], limit=1)
        return journal

    journal_id = fields.Many2one(
        "account.journal",
        string="Salary Journal",
        default=_default_journal_id,
        domain=[("type", "=", "general")],
    )
