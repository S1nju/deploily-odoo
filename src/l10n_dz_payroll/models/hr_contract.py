# Part of OCA. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrContract(models.Model):
    """
    Extension du contrat de travail pour la réglementation algérienne.
    Ajoute les champs nécessaires au calcul de la paie algérienne.
    """

    _inherit = "hr.contract"

    # ── Identification salarié ────────────────────────────────────────────────
    matricule = fields.Char(
        string="Matricule",
        help="Numéro matricule de l'employé",
    )
    numero_cnas = fields.Char(
        string="N° CNAS",
        help="Numéro d'affiliation CNAS de l'employé",
    )
    numero_compte_bancaire = fields.Char(
        string="N° Compte Bancaire / CCP",
        help="Numéro de compte bancaire ou CCP pour virement salaire",
    )

    # ── Classification ────────────────────────────────────────────────────────
    grade = fields.Char(string="Grade")
    categorie_professionnelle = fields.Char(
        string="Catégorie Professionnelle",
        help="Ex: Cadre, Agent de maîtrise, Ouvrier qualifié, etc.",
    )
    poste_occupe = fields.Char(string="Poste occupé")

    # ── Salaire ───────────────────────────────────────────────────────────────
    salaire_de_poste = fields.Monetary(
        string="Salaire de poste (DA)",
        help="Salaire de base afférent au poste occupé",
    )

    # ── Primes & indemnités contractuelles ────────────────────────────────────
    prime_rendement = fields.Monetary(
        string="Prime de rendement (DA)",
    )
    prime_astreinte = fields.Monetary(
        string="Prime d'astreinte (DA)",
    )
    indemnite_nuisance = fields.Monetary(
        string="Indemnité de nuisance (DA)",
    )
    prime_panier_contractuelle = fields.Monetary(
        string="Indemnité panier contractuelle (DA)",
    )

    # ── Jours ouvrables ───────────────────────────────────────────────────────
    jours_ouvrables = fields.Float(
        string="Jours ouvrables / mois",
        default=26.0,
        help="Nombre de jours ouvrables par mois (défaut : 26)",
    )

    # ── Ancienneté ────────────────────────────────────────────────────────────
    date_recrutement = fields.Date(
        string="Date de recrutement",
        help="Date d'entrée dans l'entreprise pour calcul ancienneté/IEP",
    )
