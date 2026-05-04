# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployee(models.Model):
    """
    Extension du modèle employé pour les besoins de la paie algérienne.
    """

    _inherit = "hr.employee"

    # ── Informations personnelles ─────────────────────────────────────────────
    situation_familiale = fields.Selection(
        [
            ("celibataire", "Célibataire"),
            ("marie", "Marié(e)"),
            ("divorce", "Divorcé(e)"),
            ("veuf", "Veuf/Veuve"),
        ],
        string="Situation familiale",
        default="celibataire",
    )
    nb_enfants_dz = fields.Integer(
        string="Nombre d'enfants à charge",
        default=0,
    )
    conjoint_travaille = fields.Boolean(
        string="Conjoint travaille",
        help="Si oui, la déduction conjoint IRG ne s'applique pas",
        default=False,
    )

    # ── Identifiants administratifs ───────────────────────────────────────────
    numero_securite_sociale = fields.Char(
        string="N° Sécurité Sociale",
        help="Numéro de sécurité sociale (CNAS)",
    )
    numero_nif = fields.Char(
        string="NIF",
        help="Numéro d'Identification Fiscale",
    )

    # ── Direction / Structure ─────────────────────────────────────────────────
    direction = fields.Char(
        string="Direction",
        help="Direction ou département d'affectation",
    )
    taux_irg = fields.Float(
        string="Taux IRG spécifique (%)",
        help="Si renseigné, ce taux fixe est utilisé à la place du barème progressif.",
    )
