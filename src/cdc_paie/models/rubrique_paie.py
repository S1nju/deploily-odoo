# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RubriquePaie(models.Model):
    """
    Plan de rubriques entièrement paramétrable (CDC requirement).
    Covers: gains, retenues, cotisations, indemnités.
    """
    _name = 'cdc.rubrique.paie'
    _description = 'Rubrique de Paie'
    _order = 'sequence, code'

    code = fields.Char(string='Code', required=True, copy=False)
    name = fields.Char(string='Libellé', required=True)
    sequence = fields.Integer(string='Séquence', default=10)

    type_rubrique = fields.Selection([
        ('gain', 'Gain / Salaire'),
        ('indemnite', 'Indemnité'),
        ('prime', 'Prime'),
        ('retenue', 'Retenue'),
        ('cotisation_sal', 'Cotisation Salariale'),
        ('cotisation_pat', 'Cotisation Patronale'),
        ('impot', 'Impôt (IRG)'),
        ('allocation', 'Allocation Familiale'),
    ], string='Type', required=True, default='gain')

    mode_calcul = fields.Selection([
        ('fixe', 'Montant Fixe'),
        ('taux_salaire', 'Taux sur Salaire de Base'),
        ('taux_brut', 'Taux sur Salaire Brut'),
        ('formule', 'Formule Personnalisée'),
        ('irg', 'Barème IRG'),
        ('cnas', 'Taux CNAS'),
    ], string='Mode de Calcul', default='fixe', required=True)

    montant_fixe = fields.Float(string='Montant Fixe (DA)')
    taux = fields.Float(string='Taux (%)')
    formule = fields.Text(
        string='Formule',
        help='Variables disponibles: salaire_base, brut, iep, nbre_enfants, jours_travailles'
    )

    # Appearance on bulletin
    apparait_bulletin = fields.Boolean(string='Apparaît sur Bulletin', default=True)
    imposable = fields.Boolean(string='Imposable (IRG)', default=False)
    cotisable_cnas = fields.Boolean(string='Cotisable CNAS', default=False)

    # Plafond CNAS
    plafond_cnas = fields.Float(string='Plafond CNAS (DA)')

    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Le code rubrique doit être unique.')
    ]

    def compute_montant(self, employe, parametrage, jours_travailles=None):
        """
        Returns the computed amount for this rubrique given an employee and parametrage.
        Called from bulletin computation.
        """
        self.ensure_one()
        salaire_base = employe.salaire_base or 0.0
        iep = employe.iep or 0.0
        nbre_enfants = employe.nbre_enfants or 0
        jours_ouvrables = parametrage.jours_ouvrables or 26
        jours_travailles = jours_travailles or jours_ouvrables

        if self.mode_calcul == 'fixe':
            return self.montant_fixe

        elif self.mode_calcul == 'taux_salaire':
            return salaire_base * (self.taux / 100.0)

        elif self.mode_calcul == 'taux_brut':
            # brut placeholder — actual brut computed after all gains
            return 0.0

        elif self.mode_calcul == 'cnas':
            base = salaire_base
            if self.plafond_cnas and base > self.plafond_cnas:
                base = self.plafond_cnas
            return base * (parametrage.taux_cnas_salarie / 100.0)

        elif self.mode_calcul == 'formule':
            try:
                local_vars = {
                    'salaire_base': salaire_base,
                    'iep': iep,
                    'nbre_enfants': nbre_enfants,
                    'jours_travailles': jours_travailles,
                    'jours_ouvrables': jours_ouvrables,
                    'brut': salaire_base + iep,
                    'taux_iep': employe.taux_iep,
                }
                result = eval(self.formule, {"__builtins__": {}}, local_vars)
                return float(result)
            except Exception:
                return 0.0

        elif self.mode_calcul == 'irg':
            # IRG computed separately in bulletin
            return 0.0

        return 0.0
