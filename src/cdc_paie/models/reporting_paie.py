# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64


class EtatPaie(models.Model):
    """
    États de paie : récapitulatifs, journal, virements, CCP, etc.
    All required outputs from CDC ERP 026-2025.
    """
    _name = 'cdc.etat.paie'
    _description = 'État de Paie'
    _inherit = ['mail.thread']
    _order = 'annee desc, mois desc'

    name = fields.Char(string='Référence', readonly=True, default='Nouveau')
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois')
    annee = fields.Integer(string='Année', required=True)

    type_etat = fields.Selection([
        # CDC required outputs
        ('recapitulatif', 'État Récapitulatif des Salaires'),
        ('journal_paie', 'Journal de Paie Mensuel'),
        ('virement_bancaire', 'Avis de Virement Bancaire'),
        ('virement_ccp', 'Avis de Virement CCP CS 102'),
        ('fichier_ccp', 'Fichier CCP (Cd) pour Banque'),
        ('etat_charges', 'État des Charges'),
        ('etat_301bis', 'État 301 Bis'),
        ('etat_journal_104', 'État Journal 104'),
        ('declaration_annuelle', 'Déclaration Annuelle des Salaires'),
        ('ats', 'Attestation du Travail et des Salaires (ATS)'),
        ('releve_carriere', 'Relevé de Carrière'),
        ('releve_emoluments', 'Relevé des Émoluments'),
        ('etat_annuel_remunerations', 'État Annuel des Rémunérations'),
        ('etat_irg', 'État d\'IRG'),
        ('cotisations_sociales', 'États des Cotisations Sociales et Fiscales'),
        ('etat_securite_sociale', 'État de Sécurité Sociale'),
        ('cnr', 'Fiche Carrière CNR (États DFC)'),
        ('etat_absences', 'État des Absences'),
        ('remboursement_avance', 'État de Remboursement (Avance sur Salaire)'),
        ('mandats', 'Mandats'),
        ('etat_comparaison_cd', 'État de Comparaison (Journal / Cd)'),
        ('etat_comparaison_mois', 'État de Comparaison (Mouvement du mois)'),
        ('situation_paiements', 'Situation des Paiements'),
        ('etat_reglement_ccp', 'État de Règlement CCP'),
        ('etat_matrice', 'État Matrice'),
        ('etat_modificatif', 'État Modificatif'),
        ('cd_paie', 'Cd Paie'),
        ('mandat_paiement', 'Mandat de Paiement'),
        ('fiche_engagement', 'Fiche d\'Engagement'),
    ], string='Type d\'État', required=True)
    
    direction_id = fields.Many2one('hr.department', string='Direction / Service')
    tous_directions = fields.Boolean(string='Tous les services', default=True)  
    categorie = fields.Selection([
        ('cadre', 'Cadre'), ('maitrise', 'Maîtrise'),
        ('execution', 'Exécution'), ('tous', 'Tous'),
    ], string='Catégorie', default='tous')

    # Résumé des totaux
    effectif = fields.Integer(string='Effectif', compute='_compute_totaux', store=True)
    total_brut = fields.Float(
        string='Total Brut (DA)', compute='_compute_totaux', store=True
    )
    total_cnas_sal = fields.Float(
        string='Total CNAS Salarié', compute='_compute_totaux', store=True
    )
    total_irg = fields.Float(
        string='Total IRG', compute='_compute_totaux', store=True
    )
    total_net = fields.Float(
        string='Total Net à Payer (DA)', compute='_compute_totaux', store=True
    )
    total_charge_patronale = fields.Float(
        string='Total Charge Patronale (DA)', compute='_compute_totaux', store=True
    )
    total_masse_salariale = fields.Float(
        string='Masse Salariale (DA)', compute='_compute_totaux', store=True
    )

    ligne_ids = fields.One2many(
        'cdc.ligne.etat.paie', 'etat_id', string='Détail'
    )
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('genere', 'Généré'),
    ], default='brouillon')

    # CCP export
    fichier_ccp = fields.Binary(string='Fichier CCP')
    fichier_ccp_name = fields.Char(string='Nom Fichier CCP')

    @api.depends('ligne_ids.salaire_brut', 'ligne_ids.cnas_salarie',
                 'ligne_ids.irg', 'ligne_ids.salaire_net',
                 'ligne_ids.charge_patronale')
    def _compute_totaux(self):
        for etat in self:
            lignes = etat.ligne_ids
            etat.effectif = len(lignes)
            etat.total_brut = sum(lignes.mapped('salaire_brut'))
            etat.total_cnas_sal = sum(lignes.mapped('cnas_salarie'))
            etat.total_irg = sum(lignes.mapped('irg'))
            etat.total_net = sum(lignes.mapped('salaire_net'))
            etat.total_charge_patronale = sum(lignes.mapped('charge_patronale'))
            etat.total_masse_salariale = etat.total_brut + etat.total_charge_patronale

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cdc.etat.paie'
                ) or 'Nouveau'
        return super().create(vals_list)

    def action_generer(self):
        """Populate lines from validated bulletins matching this state's filters."""
        for etat in self:
            etat.ligne_ids.unlink()
            domain = [('state', 'in', ('valide', 'paye')), ('annee', '=', etat.annee)]
            if etat.mois:
                domain.append(('mois', '=', etat.mois))
            if etat.direction_id:
                domain.append(('direction_id', '=', etat.direction_id.id))
            bulletins = self.env['cdc.bulletin.paie'].search(domain)
            lignes = []
            for b in bulletins:
                lignes.append({
                    'etat_id': etat.id,
                    'employe_id': b.employe_id.id,
                    'matricule': b.matricule,
                    'grade': b.grade,
                    'fonction': b.fonction,
                    'categorie': b.categorie,
                    'salaire_base': b.salaire_base,
                    'salaire_brut': b.salaire_brut,
                    'cnas_salarie': b.cnas_salarie,
                    'cnas_patronal': b.cnas_patronal,
                    'irg': b.irg,
                    'allocation_familiale': b.allocation_familiale,
                    'salaire_net': b.salaire_net,
                    'charge_patronale': b.charge_patronale,
                    'moyen_paiement': b.moyen_paiement,
                    'num_compte': b.num_compte,
                    'mois': b.mois,
                })
            self.env['cdc.ligne.etat.paie'].create(lignes)
            etat.state = 'genere'
            # Auto-generate CCP file if applicable
            if etat.type_etat in ('fichier_ccp', 'virement_ccp'):
                etat._generer_fichier_ccp()

    def _generer_fichier_ccp(self):
        """Generate flat CCP transfer file (Cd format)."""
        lines_ccp = self.ligne_ids.filtered(
            lambda l: l.moyen_paiement in ('ccp', 'virement')
        )
        content = ""
        for l in lines_ccp:
            num_compte = (l.num_compte or '').ljust(20)
            nom = (l.employe_id.name or '').ljust(40)
            montant = f"{l.salaire_net:.2f}".rjust(15)
            content += f"{num_compte}{nom}{montant}\n"
        encoded = base64.b64encode(content.encode('utf-8'))
        self.fichier_ccp = encoded
        self.fichier_ccp_name = f"CCP_{self.annee}_{self.mois or 'ANNUEL'}.txt"

    def action_telecharger_ccp(self):
        if not self.fichier_ccp:
            raise UserError(_("Veuillez d'abord générer l'état."))
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=cdc.etat.paie&id={self.id}'
                   f'&field=fichier_ccp&filename={self.fichier_ccp_name}&download=true',
            'target': 'self',
        }


class LigneEtatPaie(models.Model):
    _name = 'cdc.ligne.etat.paie'
    _description = 'Ligne État de Paie'
    _order = 'employe_id'

    etat_id = fields.Many2one('cdc.etat.paie', ondelete='cascade')
    employe_id = fields.Many2one('hr.employee', string='Employé')
    matricule = fields.Char(string='Matricule')
    grade = fields.Char(string='Grade')
    fonction = fields.Char(string='Fonction')
    categorie = fields.Char(string='Catégorie')
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois')
    salaire_base = fields.Float(string='Salaire de Base')
    salaire_brut = fields.Float(string='Salaire Brut')
    cnas_salarie = fields.Float(string='CNAS Salarié')
    cnas_patronal = fields.Float(string='CNAS Patronal')
    irg = fields.Float(string='IRG')
    allocation_familiale = fields.Float(string='Allocations Familiales')
    salaire_net = fields.Float(string='Net à Payer')
    charge_patronale = fields.Float(string='Charge Patronale')
    moyen_paiement = fields.Selection([
        ('ccp', 'CCP'), ('virement', 'Virement'), ('especes', 'Espèces'),
        ('mandat', 'Mandat'),
    ], string='Moyen de Paiement')
    num_compte = fields.Char(string='N° Compte')