# -*- coding: utf-8 -*-
"""
wizard_flux.py – Trésorerie Pro / Odoo 18
==========================================
Wizard unique pour créer un flux (une seule fois ou récurrent).
S'ouvre depuis le bouton "Nouveau" de la liste des flux.
"""
import logging
from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WizardFlux(models.TransientModel):
    _name = 'wizard.recurrence.tresorerie'
    _description = "Créer un flux de trésorerie"

    label = fields.Char(string="Désignation", required=True)
    partner_id = fields.Many2one('res.partner', string="Partenaire")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    compte_id = fields.Many2one('compte.tresorerie', string="Compte", required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    type_mouvement = fields.Selection(
        [('entree', 'Entrée (+)'), ('sortie', 'Sortie (-)')],
        string="Type", required=True, default='entree',
    )
    montant = fields.Monetary(string="Montant", currency_field='currency_id', required=True)

    type_recurrence = fields.Selection(
        [('once', 'Une seule fois'),
         ('jour', 'Chaque jour'),
         ('semaine', 'Chaque semaine'),
         ('mois', 'Chaque mois')],
        string="Fréquence", required=True, default='once',
    )

    # For once
    date_prevue = fields.Datetime(
        string="Date", default=fields.Datetime.now, required=True,
    )

    # For recurring
    date_debut = fields.Datetime(string="Date de début", default=fields.Datetime.now)
    date_fin = fields.Datetime(string="Date de fin")
    jour_semaine = fields.Selection([
        ('0', 'Lundi'), ('1', 'Mardi'), ('2', 'Mercredi'),
        ('3', 'Jeudi'), ('4', 'Vendredi'), ('5', 'Samedi'), ('6', 'Dimanche'),
    ], string="Jour de la semaine")
    jour_mois = fields.Selection(
        [(str(d), str(d)) for d in range(1, 32)],
        string="Jour du mois",
    )

    def _build_vals(self, dt):
        entree = self.montant if self.type_mouvement == 'entree' else 0.0
        sortie = self.montant if self.type_mouvement == 'sortie' else 0.0
        recurrence = self.type_recurrence if self.type_recurrence != 'once' else False
        return {
            'label': self.label,
            'compte_id': self.compte_id.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'montant_entree': entree,
            'montant_sortie': sortie,
            'date_prevue': dt,
            'date': dt,
            'state': 'prevu',
            'type_recurrence': recurrence,
            'date_debut': self.date_debut if recurrence else False,
            'date_fin': self.date_fin if recurrence else False,
        }

    def action_creer_flux(self):
        self.ensure_one()
        Flux = self.env['flux.tresorerie']

        if self.type_recurrence == 'once':
            Flux.create(self._build_vals(self.date_prevue))

        else:
            if not self.date_debut or not self.date_fin:
                raise UserError("Veuillez renseigner la date de début et de fin.")
            delta = self.date_fin - self.date_debut
            if delta.days < 0:
                raise UserError("La date de début doit être antérieure à la date de fin.")

            interval = [self.date_debut + timedelta(days=i) for i in range(delta.days + 1)]

            if self.type_recurrence == 'jour':
                dates = interval
            elif self.type_recurrence == 'semaine':
                if not self.jour_semaine:
                    raise UserError("Veuillez sélectionner un jour de la semaine.")
                target = int(self.jour_semaine)
                dates = [d for d in interval if d.weekday() == target]
            elif self.type_recurrence == 'mois':
                if not self.jour_mois:
                    raise UserError("Veuillez sélectionner un jour du mois.")
                target = int(self.jour_mois)
                dates = [d for d in interval if d.day == target]
                if not dates:
                    raise UserError(f"Le jour {self.jour_mois} n'existe pas dans l'intervalle.")
            else:
                dates = []

            if not dates:
                raise UserError("Aucune occurrence trouvée pour la récurrence choisie.")

            for dt in dates:
                Flux.create(self._build_vals(dt))

            _logger.info("WizardFlux: %d flux créé(s) pour '%s'.", len(dates), self.compte_id.name)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Flux de trésorerie',
            'res_model': 'flux.tresorerie',
            'view_mode': 'list,form',
            'domain': [('compte_id', '=', self.compte_id.id)],
        }
