# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardGenererBulletins(models.TransientModel):
    """
    Mass bulletin generation wizard.
    Creates one bulletin per active employee for the selected period.
    """
    _name = 'cdc.wizard.generer.bulletins'
    _description = 'Générer les Bulletins de Paie en Masse'

    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True,
        default=lambda self: str(fields.Date.today().month))
    annee = fields.Integer(
        string='Année', required=True,
        default=lambda self: fields.Date.today().year
    )
    parametrage_id = fields.Many2one(
        'cdc.parametrage.paie', string='Paramétrage', required=True
    )
    type_bulletin = fields.Selection([
        ('salaire', 'Salaire'),
        ('rappel', 'Rappel'),
        ('prime_prc', 'Prime (PRI-PRC)'),
    ], string='Type de Bulletin', default='salaire', required=True)

    direction_ids = fields.Many2many(
        'hr.department', string='Filtrer par Direction(s)',
        help='Laisser vide pour générer pour tous les employés actifs.'
    )
    ecrase_existants = fields.Boolean(
        string='Écraser les bulletins existants (brouillon)',
        default=False
    )

    nb_employes = fields.Integer(
        string='Employés concernés', compute='_compute_nb_employes'
    )

    @api.depends('direction_ids')
    def _compute_nb_employes(self):
        for wiz in self:
            domain = [('active', '=', True)]
            if wiz.direction_ids:
                domain.append(('department_id', 'in', wiz.direction_ids.ids))
            wiz.nb_employes = self.env['hr.employee'].search_count(domain)

    def action_generer(self):
        self.ensure_one()
        domain = [('active', '=', True)]
        if self.direction_ids:
            domain.append(('department_id', 'in', self.direction_ids.ids))
        employes = self.env['hr.employee'].search(domain)

        if not employes:
            raise UserError(_("Aucun employé actif trouvé avec ces critères."))

        Bulletin = self.env['cdc.bulletin.paie']
        created = self.env['cdc.bulletin.paie']

        for emp in employes:
            # Check existing
            existing = Bulletin.search([
                ('employe_id', '=', emp.id),
                ('mois', '=', self.mois),
                ('annee', '=', self.annee),
                ('type_bulletin', '=', self.type_bulletin),
            ], limit=1)

            if existing:
                if self.ecrase_existants and existing.state == 'brouillon':
                    existing.unlink()
                else:
                    continue

            bulletin = Bulletin.create({
                'employe_id': emp.id,
                'mois': self.mois,
                'annee': self.annee,
                'type_bulletin': self.type_bulletin,
                'parametrage_id': self.parametrage_id.id,
                'jours_ouvrables': self.parametrage_id.jours_ouvrables,
                'jours_travailles': self.parametrage_id.jours_ouvrables,
            })
            bulletin.action_calculer()
            created |= bulletin

        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulletins Générés (%d)') % len(created),
            'res_model': 'cdc.bulletin.paie',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created.ids)],
        }
