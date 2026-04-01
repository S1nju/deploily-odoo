# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64


class DeclarationCNAS(models.Model):
    """
    Déclaration CNAS mensuelle & annuelle (G50 + G29)
    Required by CDC ERP 026-2025.
    """
    _name = 'cdc.declaration.cnas'
    _description = 'Déclaration CNAS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'annee desc, mois desc'

    name = fields.Char(string='Référence', readonly=True, default='Nouveau')
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True)
    annee = fields.Integer(string='Année', required=True)
    type_declaration = fields.Selection([
        ('mensuelle', 'Mensuelle (G50)'),
        ('trimestrielle', 'Trimestrielle'),
        ('annuelle', 'Annuelle (G29)'),
    ], string='Type', required=True, default='mensuelle')
    parametrage_id = fields.Many2one('cdc.parametrage.paie', string='Paramétrage')

    # Totaux
    effectif = fields.Integer(string='Effectif', compute='_compute_totaux', store=True)
    montant_cotisable = fields.Float(
        string='Montant Cotisable Total (DA)', compute='_compute_totaux', store=True
    )
    total_cnas_salarie = fields.Float(
        string='Total CNAS Salarié (DA)', compute='_compute_totaux', store=True
    )
    total_cnas_patronal = fields.Float(
        string='Total CNAS Patronal (DA)', compute='_compute_totaux', store=True
    )
    total_cnas = fields.Float(
        string='Total CNAS (DA)', compute='_compute_totaux', store=True
    )
    num_affiliation = fields.Char(string='N° Affiliation CNAS')
    taux_irg = fields.Float(string='Taux IRG (%)')

    ligne_ids = fields.One2many(
        'cdc.ligne.declaration.cnas', 'declaration_id', string='Lignes'
    )
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('genere', 'Généré'),
        ('soumis', 'Soumis'),
    ], default='brouillon', string='État')

    @api.depends('ligne_ids.montant_cotisable',
                 'ligne_ids.cnas_salarie', 'ligne_ids.cnas_patronal')
    def _compute_totaux(self):
        for decl in self:
            lignes = decl.ligne_ids
            decl.effectif = len(lignes)
            decl.montant_cotisable = sum(lignes.mapped('montant_cotisable'))
            decl.total_cnas_salarie = sum(lignes.mapped('cnas_salarie'))
            decl.total_cnas_patronal = sum(lignes.mapped('cnas_patronal'))
            decl.total_cnas = decl.total_cnas_salarie + decl.total_cnas_patronal

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cdc.declaration.cnas'
                ) or 'Nouveau'
        return super().create(vals_list)

    def action_generer(self):
        """Generate declaration lines from validated bulletins of the period."""
        for decl in self:
            # Remove existing lines
            decl.ligne_ids.unlink()
            bulletins = self.env['cdc.bulletin.paie'].search([
                ('mois', '=', decl.mois),
                ('annee', '=', decl.annee),
                ('state', 'in', ('valide', 'paye')),
            ])
            lignes = []
            for b in bulletins:
                lignes.append({
                    'declaration_id': decl.id,
                    'employe_id': b.employe_id.id,
                    'matricule': b.matricule,
                    'num_affiliation': b.num_cnas,
                    'salaire_base': b.salaire_base,
                    'montant_cotisable': b.montant_cotisable,
                    'cnas_salarie': b.cnas_salarie,
                    'cnas_patronal': b.cnas_patronal,
                })
            self.env['cdc.ligne.declaration.cnas'].create(lignes)
            decl.state = 'genere'

    def action_imprimer(self):
        return self.env.ref('cdc_paie.action_report_cnas').report_action(self)


class LigneDeclarationCNAS(models.Model):
    _name = 'cdc.ligne.declaration.cnas'
    _description = 'Ligne Déclaration CNAS'

    declaration_id = fields.Many2one(
        'cdc.declaration.cnas', ondelete='cascade'
    )
    employe_id = fields.Many2one('hr.employee', string='Employé')
    matricule = fields.Char(string='Matricule')
    num_affiliation = fields.Char(string='N° Affiliation')
    salaire_base = fields.Float(string='Salaire de Base')
    montant_cotisable = fields.Float(string='Montant Cotisable')
    cnas_salarie = fields.Float(string='CNAS Salarié')
    cnas_patronal = fields.Float(string='CNAS Patronal')
    total_cnas = fields.Float(
        string='Total CNAS', compute='_compute_total', store=True
    )

    @api.depends('cnas_salarie', 'cnas_patronal')
    def _compute_total(self):
        for l in self:
            l.total_cnas = l.cnas_salarie + l.cnas_patronal


class DeclarationIRG(models.Model):
    """
    Déclaration IRG mensuelle et annuelle (G50 / État 301 bis).
    """
    _name = 'cdc.declaration.irg'
    _description = 'Déclaration IRG'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'annee desc, mois desc'

    name = fields.Char(string='Référence', readonly=True, default='Nouveau')
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois')
    annee = fields.Integer(string='Année', required=True)
    type_declaration = fields.Selection([
        ('mensuelle', 'Mensuelle'),
        ('annuelle', 'Annuelle'),
    ], string='Type', default='mensuelle', required=True)

    total_base_irg = fields.Float(
        string='Total Base IRG (DA)', compute='_compute_totaux', store=True
    )
    total_irg = fields.Float(
        string='Total IRG (DA)', compute='_compute_totaux', store=True
    )
    effectif = fields.Integer(
        string='Effectif', compute='_compute_totaux', store=True
    )

    ligne_ids = fields.One2many(
        'cdc.ligne.declaration.irg', 'declaration_id', string='Lignes'
    )
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('genere', 'Généré'),
        ('soumis', 'Soumis'),
    ], default='brouillon')

    @api.depends('ligne_ids.base_irg', 'ligne_ids.irg')
    def _compute_totaux(self):
        for decl in self:
            decl.total_base_irg = sum(decl.ligne_ids.mapped('base_irg'))
            decl.total_irg = sum(decl.ligne_ids.mapped('irg'))
            decl.effectif = len(decl.ligne_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cdc.declaration.irg'
                ) or 'Nouveau'
        return super().create(vals_list)

    def action_generer(self):
        for decl in self:
            decl.ligne_ids.unlink()
            domain = [('annee', '=', decl.annee), ('state', 'in', ('valide', 'paye'))]
            if decl.type_declaration == 'mensuelle' and decl.mois:
                domain.append(('mois', '=', decl.mois))
            bulletins = self.env['cdc.bulletin.paie'].search(domain)
            lignes = []
            for b in bulletins:
                lignes.append({
                    'declaration_id': decl.id,
                    'employe_id': b.employe_id.id,
                    'matricule': b.matricule,
                    'salaire_brut': b.salaire_brut,
                    'base_irg': b.base_irg,
                    'irg': b.irg,
                    'mois': b.mois,
                })
            self.env['cdc.ligne.declaration.irg'].create(lignes)
            decl.state = 'genere'

    def action_imprimer(self):
        return self.env.ref('cdc_paie.action_report_irg').report_action(self)


class LigneDeclarationIRG(models.Model):
    _name = 'cdc.ligne.declaration.irg'
    _description = 'Ligne Déclaration IRG'

    declaration_id = fields.Many2one('cdc.declaration.irg', ondelete='cascade')
    employe_id = fields.Many2one('hr.employee', string='Employé')
    matricule = fields.Char(string='Matricule')
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois')
    salaire_brut = fields.Float(string='Salaire Brut')
    base_irg = fields.Float(string='Base IRG')
    irg = fields.Float(string='IRG')
