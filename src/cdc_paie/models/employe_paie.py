# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EmployePaie(models.Model):
    """
    Fiche Salarié (paie) — extends hr.employee with all payroll-specific fields
    required by CDC ERP 026-2025.
    """
    _inherit = 'hr.employee'

    # ── Identification ──────────────────────────────────────────────────────
    matricule = fields.Char(string='Matricule', copy=False)
    num_cnas = fields.Char(string='Numéro CNAS / Affiliation')
    num_ccp = fields.Char(string='Numéro CCP')
    num_compte_bancaire = fields.Char(string='Numéro Compte Bancaire')
    num_securite_sociale = fields.Char(string='N° Sécurité Sociale')

    # ── Classification ───────────────────────────────────────────────────────
    grade = fields.Char(string='Grade')
    categorie_sociopro = fields.Selection([
        ('cadre', 'Cadre'),
        ('maitrise', 'Maîtrise'),
        ('execution', 'Exécution'),
        ('stagiaire', 'Stagiaire'),
    ], string='Catégorie Socioprofessionnelle')

    # ── Contrat / Poste ───────────────────────────────────────────────────────
    type_contrat = fields.Selection([
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('vacataire', 'Vacataire'),
        ('stagiaire', 'Stagiaire'),
    ], string='Type de Contrat')
    date_recrutement = fields.Date(string='Date de Recrutement')
    poste_occupe = fields.Char(string='Poste Occupé')

    # ── Situation Familiale ───────────────────────────────────────────────────
    nbre_enfants = fields.Integer(string='Nombre d\'Enfants', default=0)
    moyen_paiement = fields.Selection([
        ('ccp', 'CCP'),
        ('virement', 'Virement Bancaire'),
        ('especes', 'Espèces'),
        ('mandat', 'Mandat'),
    ], string='Moyen de Paiement', default='virement')

    # ── Salaire de Base ───────────────────────────────────────────────────────
    salaire_base = fields.Float(string='Salaire de Base (DA)')
    salaire_poste = fields.Float(string='Salaire de Poste (DA)')

    # ── Taux IEP ─────────────────────────────────────────────────────────────
    taux_iep = fields.Float(string='Taux IEP (%)', default=0.0)
    iep = fields.Float(string='IEP (DA)', compute='_compute_iep', store=True)

    # ── Primes et retenues ────────────────────────────────────────────────────
    prime_responsabilite = fields.Float(string='Prime de Responsabilité (DA)')
    prime_sujetion = fields.Float(string='Prime de Sujétion (DA)')
    prime_ifsp = fields.Float(string='Prime IFSP (DA)')
    indemnites_variables = fields.Float(string='Indemnités Variables (DA)')

    # ── Retards ───────────────────────────────────────────────────────────────
    retards = fields.Float(string='Retards (heures)')

    # ── Historique contrats ───────────────────────────────────────────────────
    historique_contrat_ids = fields.One2many(
        'cdc.historique.contrat', 'employe_id', string='Historique des Contrats'
    )

    # ── Computed ─────────────────────────────────────────────────────────────
    @api.depends('salaire_base', 'taux_iep')
    def _compute_iep(self):
        for emp in self:
            emp.iep = emp.salaire_base * (emp.taux_iep / 100.0)

    # ── Bulletin count ────────────────────────────────────────────────────────
    bulletin_count = fields.Integer(
        string='Bulletins', compute='_compute_bulletin_count'
    )

    def _compute_bulletin_count(self):
        BulletinModel = self.env['cdc.bulletin.paie']
        for emp in self:
            emp.bulletin_count = BulletinModel.search_count(
                [('employe_id', '=', emp.id)]
            )

    def action_view_bulletins(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bulletins de Paie',
            'res_model': 'cdc.bulletin.paie',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }


class HistoriqueContrat(models.Model):
    _name = 'cdc.historique.contrat'
    _description = 'Historique des Contrats'
    _order = 'date_debut desc'

    employe_id = fields.Many2one('hr.employee', string='Employé', ondelete='cascade')
    type_contrat = fields.Selection([
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('renouvellement', 'Renouvellement'),
        ('vacataire', 'Vacataire'),
        ('stagiaire', 'Stagiaire'),
    ], string='Type de Contrat', required=True)
    date_debut = fields.Date(string='Date Début', required=True)
    date_fin = fields.Date(string='Date Fin')
    salaire_base = fields.Float(string='Salaire de Base')
    grade = fields.Char(string='Grade')
    poste = fields.Char(string='Poste')
    notes = fields.Text(string='Notes / Évolutions')
