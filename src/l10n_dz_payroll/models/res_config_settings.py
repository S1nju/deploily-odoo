# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_dz_payroll_rate_id = fields.Many2one(
        "l10n.dz.hr.payroll.rate",
        string="Taux légaux actifs",
        help="Taux légaux algériens utilisés pour les calculs de paie",
        config_parameter="l10n_dz_payroll.rate_id",
    )
