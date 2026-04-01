# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64


class WizardVirement(models.TransientModel):
    """
    Wizard to generate bank / CCP transfer file for a given pay period.
    Required by CDC ERP 026-2025: Avis de virement bancaire / CCP CS 102 / Fichier Cd.
    """
    _name = 'cdc.wizard.virement'
    _description = 'Générer Fichier de Virement'

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
    type_virement = fields.Selection([
        ('ccp', 'Virement CCP (CS 102)'),
        ('banque', 'Virement Bancaire'),
        ('cd', 'Fichier Cd (transmission banque)'),
        ('mandat', 'Mandats de Paiement'),
    ], string='Type', required=True, default='ccp')

    fichier = fields.Binary(string='Fichier Généré', readonly=True)
    fichier_name = fields.Char(string='Nom du Fichier', readonly=True)
    nb_beneficiaires = fields.Integer(string='Bénéficiaires', readonly=True)
    total_net = fields.Float(string='Total Net (DA)', readonly=True)
    state = fields.Selection([
        ('draft', 'Prêt'), ('done', 'Généré')
    ], default='draft')

    def action_generer(self):
        self.ensure_one()
        moyen_map = {
            'ccp': 'ccp',
            'banque': 'virement',
            'cd': 'virement',
            'mandat': 'mandat',
        }
        moyen = moyen_map.get(self.type_virement, 'virement')

        bulletins = self.env['cdc.bulletin.paie'].search([
            ('mois', '=', self.mois),
            ('annee', '=', self.annee),
            ('state', 'in', ('valide', 'paye')),
            ('moyen_paiement', '=', moyen),
        ])
        if not bulletins:
            raise UserError(
                _("Aucun bulletin validé trouvé pour cette période avec ce moyen de paiement.")
            )

        lines = []
        total = 0.0
        for b in bulletins:
            compte = (b.num_compte or '').ljust(20)[:20]
            nom = (b.employe_id.name or '').ljust(40)[:40]
            montant_str = f"{b.salaire_net:.2f}".rjust(15)
            matricule = (b.matricule or '').ljust(10)[:10]
            lines.append(f"{matricule}{compte}{nom}{montant_str}")
            total += b.salaire_net

        content = "\n".join(lines) + "\n"
        content += f"{'TOTAL':>65}{total:.2f}".rjust(80) + "\n"

        encoded = base64.b64encode(content.encode('utf-8'))
        mois_label = dict(self._fields['mois'].selection).get(self.mois, self.mois)
        fname = f"VIREMENT_{self.type_virement.upper()}_{mois_label}_{self.annee}.txt"

        self.fichier = encoded
        self.fichier_name = fname
        self.nb_beneficiaires = len(bulletins)
        self.total_net = total
        self.state = 'done'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cdc.wizard.virement',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
