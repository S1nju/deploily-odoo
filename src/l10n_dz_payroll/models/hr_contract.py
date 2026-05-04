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

    # ── OUI CNAS / OUI IRG ────────────────────────────────────────────────────
    # N°2 - Salaire partie fixe Cadre Dirigeant
    salaire_fixe_cadre_dirigeant = fields.Monetary(
        string="Salaire partie fixe Cadre Dirigeant (DA)",
    )
    # N°3 - Salaire partie variable Cadre Dirigeant
    salaire_variable_cadre_dirigeant = fields.Monetary(
        string="Salaire partie variable Cadre Dirigeant (DA)",
    )
    # N°5 - Indemnité de Travail Posté
    indemnite_travail_poste = fields.Monetary(
        string="Indemnité de Travail Posté (DA)",
    )
    # N°6 - Indemnité Forfaitaire de Service Permanent
    indemnite_service_permanent = fields.Monetary(
        string="Indemnité Forfaitaire de Service Permanent (DA)",
    )
    # N°7 - Indemnité de Nuisance
    indemnite_nuisance = fields.Monetary(
        string="Indemnité de Nuisance (DA)",
    )
    # N°8 - Indemnité de Travail de Nuit
    indemnite_nuit = fields.Monetary(
        string="Indemnité de Travail de Nuit (DA)",
    )
    # N°9 - Indemnité d'Intérim
    indemnite_interim = fields.Monetary(
        string="Indemnité d'Intérim (DA)",
    )
    # N°10 - Prime de Permanence
    prime_permanence = fields.Monetary(
        string="Prime de Permanence (DA)",
    )
    # N°11 - Indemnité Forfaitaire de Fonction
    indemnite_fonction = fields.Monetary(
        string="Indemnité Forfaitaire de Fonction (DA)",
    )
    # N°12 - Indemnité de Caisse
    indemnite_caisse = fields.Monetary(
        string="Indemnité de Caisse (DA)",
    )
    # N°13 - Indemnité de Sujétion Spéciale
    indemnite_sujetion = fields.Monetary(
        string="Indemnité de Sujétion Spéciale (DA)",
    )
    # N°14 - Indemnité d'Astreinte
    indemnite_astreinte = fields.Monetary(
        string="Indemnité d'Astreinte (DA)",
    )
    # N°15 - Heures Supplémentaires
    heures_supplementaires = fields.Monetary(
        string="Heures Supplémentaires (DA)",
    )
    # N°16 - Indemnité de Congé Annuel
    indemnite_conge = fields.Monetary(
        string="Indemnité de Congé Annuel (DA)",
    )
    # N°17 - Prime d'Inventaire
    prime_inventaire = fields.Monetary(
        string="Prime d'Inventaire (DA)",
    )
    # N°18 - Prime de Bilan
    prime_bilan = fields.Monetary(
        string="Prime de Bilan (DA)",
    )
    # N°19 - PRI
    prime_rendement = fields.Monetary(
        string="PRI - Prime de Rendement (DA)",
    )
    # N°20 - PRC
    prime_prc = fields.Monetary(
        string="PRC - Prime de Résultats Collectifs (DA)",
    )

    # ── NON CNAS / OUI IRG ───────────────────────────────────────────────────
    # N°21 - Indemnité de Départ en Retraite
    indemnite_retraite = fields.Monetary(
        string="Indemnité de Départ en Retraite (DA)",
    )
    # N°25 - Panier
    prime_panier_contractuelle = fields.Monetary(
        string="Panier (DA)",
        help="Si vide, le taux légal sera utilisé",
    )
    # N°26 - Transport (géré par les taux légaux, pas de champ contrat)
    # N°27 - Prime de Mariage
    prime_mariage = fields.Monetary(
        string="Prime de Mariage (DA)",
    )
    # N°28 - Prime d'Utilisation du Véhicule Personnel
    prime_vehicule = fields.Monetary(
        string="Prime d'Utilisation du Véhicule Personnel (DA)",
    )

    # ── NON CNAS / NON IRG ───────────────────────────────────────────────────
    # N°22 - Indemnité de Décès
    indemnite_deces = fields.Monetary(
        string="Indemnité de Décès (DA)",
    )
    # N°23 - Prime de Scolarité
    prime_scolarite = fields.Monetary(
        string="Prime de Scolarité (DA)",
    )
    # N°24 - Salaire Unique (calculé automatiquement selon situation familiale)
    # N°29 - Frais de Mission
    frais_mission = fields.Monetary(
        string="Frais de Mission (DA)",
    )
    # N°30 - Prime de Zone Géographique (Isolement)
    prime_zone = fields.Monetary(
        string="Prime de Zone Géographique - Isolement (DA)",
    )
    # N°31 - Indemnité de Licenciement
    indemnite_licenciement = fields.Monetary(
        string="Indemnité de Licenciement (DA)",
    )
    # N°32 - Allocations Familiales (calculées automatiquement)

    # ── Kept for backward compatibility ──────────────────────────────────────
    prime_astreinte = fields.Monetary(
        string="Prime d'Astreinte (DA)",
    )

    # ── Famille ───────────────────────────────────────────────────────────────
    nombre_enfants = fields.Integer(
        string="Nombre d'Enfants à charge",
        default=0,
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