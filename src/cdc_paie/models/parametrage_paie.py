# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ParametragePaie(models.Model):
    _name = 'cdc.parametrage.paie'
    _description = 'Paramétrage de la Paie'
    _rec_name = 'annee'

    annee = fields.Integer(string='Année', required=True)
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True)
    date_debut = fields.Date(string='Date Début')
    date_fin = fields.Date(string='Date Fin')

    # SMIG
    smig = fields.Float(string='SMIG (DA)', default=20000.0)

    # CNAS
    taux_cnas_salarie = fields.Float(string='Taux CNAS Salarié (%)', default=9.0)
    taux_cnas_patronal = fields.Float(string='Taux CNAS Patronal (%)', default=26.0)
    plafond_cnas = fields.Float(string='Plafond CNAS (DA)', default=0.0)

    # IRG
    taux_irg_ids = fields.One2many(
        'cdc.tranche.irg', 'parametrage_id', string='Tranches IRG'
    )

    # Indemnités légales
    indemnite_panier = fields.Float(string='Indemnité de Panier (DA)', default=0.0)
    indemnite_transport = fields.Float(string='Indemnité de Transport (DA)', default=0.0)

    # Jours ouvrables
    jours_ouvrables = fields.Integer(string='Jours Ouvrables / Mois', default=26)

    # Allocation familiale
    taux_allocation_familiale = fields.Float(
        string='Allocation Familiale / Enfant (DA)', default=600.0
    )

    # IEP
    taux_iep = fields.Float(string='Taux IEP (%)', default=0.0)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('closed', 'Clôturé'),
    ], string='État', default='draft')

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_period', 'unique(annee, mois)',
         'Un paramétrage existe déjà pour cette période (mois/année).')
    ]

    def action_confirm(self):
        self.state = 'confirmed'

    def action_close(self):
        self.state = 'closed'

    def action_draft(self):
        self.state = 'draft'

    @api.model
    def get_current_parametrage(self):
        today = fields.Date.today()
        return self.search([
            ('annee', '=', today.year),
            ('mois', '=', str(today.month)),
            ('state', '=', 'confirmed'),
        ], limit=1)


class TrancheIRG(models.Model):
    _name = 'cdc.tranche.irg'
    _description = 'Tranches IRG'
    _order = 'tranche_min asc'

    parametrage_id = fields.Many2one(
        'cdc.parametrage.paie', string='Paramétrage', ondelete='cascade'
    )
    tranche_min = fields.Float(string='Tranche Min (DA)', required=True)
    tranche_max = fields.Float(string='Tranche Max (DA)', required=True)
    taux = fields.Float(string='Taux (%)', required=True)
    deduction = fields.Float(string='Déduction (DA)', default=0.0)

    @api.constrains('tranche_min', 'tranche_max')
    def _check_tranches(self):
        for rec in self:
            if rec.tranche_min >= rec.tranche_max:
                raise ValidationError(
                    "La tranche minimale doit être inférieure à la tranche maximale."
                )


class CalendrierPaie(models.Model):
    _name = 'cdc.calendrier.paie'
    _description = 'Calendrier de Paie'

    name = fields.Char(string='Libellé', required=True)
    annee = fields.Integer(string='Année', required=True)
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True)
    date_traitement = fields.Date(string='Date de Traitement', required=True)
    date_paiement = fields.Date(string='Date de Paiement')
    state = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_cours', 'En Cours'),
        ('cloture', 'Clôturé'),
    ], default='planifie', string='État')
    notes = fields.Text(string='Notes')
