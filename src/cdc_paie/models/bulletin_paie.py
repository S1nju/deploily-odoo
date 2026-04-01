# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class BulletinPaie(models.Model):
    """
    Bulletin de Paie — CDC ERP 026-2025
    Covers:
      - Calcul automatique Brut / Net / Charge patronale
      - Cotisations CNAS (salariale + patronale)
      - IRG (barème progressif)
      - IEP, indemnités, primes, retenues
      - Allocations familiales
      - Congés payés
    """
    _name = 'cdc.bulletin.paie'
    _description = 'Bulletin de Paie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'annee desc, mois desc, employe_id'

    # ── En-tête ───────────────────────────────────────────────────────────────
    name = fields.Char(
        string='Référence', readonly=True, copy=False, default='Nouveau'
    )
    employe_id = fields.Many2one(
        'hr.employee', string='Employé', required=True,
        tracking=True, ondelete='restrict'
    )
    direction_id = fields.Many2one(
        'hr.department', string='Direction / Service',
        related='employe_id.department_id', store=True
    )
    matricule = fields.Char(
        related='employe_id.matricule', string='Matricule', store=True
    )
    grade = fields.Char(
        related='employe_id.grade', string='Grade', store=True
    )
    # ✅ الإصلاح الوحيد — compute بدل related على حقل مترجم
    fonction = fields.Char(
        string='Fonction', compute='_compute_fonction', store=True
    )
    categorie = fields.Selection(
        related='employe_id.categorie_sociopro', string='Catégorie', store=True
    )
    situation_familiale = fields.Selection(
        related='employe_id.marital', string='Situation Familiale', store=True
    )
    nbre_enfants = fields.Integer(
        related='employe_id.nbre_enfants', string='Nbre d\'Enfants', store=True
    )
    num_securite_sociale = fields.Char(
        related='employe_id.num_securite_sociale', store=True
    )
    num_cnas = fields.Char(related='employe_id.num_cnas', store=True)
    moyen_paiement = fields.Selection(
        related='employe_id.moyen_paiement', store=True
    )
    num_compte = fields.Char(related='employe_id.num_compte_bancaire', store=True)

    # ── Période ───────────────────────────────────────────────────────────────
    mois = fields.Selection([
        ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
        ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'),
        ('7', 'Juillet'), ('8', 'Août'), ('9', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True, tracking=True)
    annee = fields.Integer(string='Année', required=True, tracking=True)

    type_bulletin = fields.Selection([
        ('salaire', 'Salaire'),
        ('rappel', 'Rappel'),
        ('prime_prc', 'Prime (PRI-PRC)'),
        ('regularisation', 'Régularisation'),
    ], string='Type de Bulletin', default='salaire', required=True)

    parametrage_id = fields.Many2one(
        'cdc.parametrage.paie', string='Paramétrage Paie', required=True
    )

    # ── Jours / Présence ─────────────────────────────────────────────────────
    jours_ouvrables = fields.Float(string='Jours Ouvrables', default=26)
    jours_travailles = fields.Float(string='Jours Travaillés', default=26)
    jours_conges = fields.Float(string='Congés Payés (jours)')
    jours_absences = fields.Float(string='Absences (jours)')
    retards_heures = fields.Float(string='Retards (heures)')

    # ── Éléments de salaire ───────────────────────────────────────────────────
    salaire_base = fields.Float(
        string='Salaire de Base (DA)',
        related='employe_id.salaire_base', store=True
    )
    salaire_poste = fields.Float(
        string='Salaire de Poste (DA)',
        related='employe_id.salaire_poste', store=True
    )
    taux_iep = fields.Float(
        string='Taux IEP (%)', related='employe_id.taux_iep', store=True
    )
    iep = fields.Float(string='IEP (DA)', compute='_compute_elements', store=True)

    # ── Indemnités ────────────────────────────────────────────────────────────
    indemnite_panier = fields.Float(string='Indemnité de Panier (DA)')
    indemnite_transport = fields.Float(string='Indemnité de Transport (DA)')
    indemnites_variables = fields.Float(string='Indemnités Variables (DA)')
    prime_responsabilite = fields.Float(
        string='Prime de Responsabilité (DA)',
        related='employe_id.prime_responsabilite', store=True
    )
    prime_sujetion = fields.Float(
        string='Prime de Sujétion (DA)',
        related='employe_id.prime_sujetion', store=True
    )
    prime_ifsp = fields.Float(
        string='Prime IFSP (DA)', related='employe_id.prime_ifsp', store=True
    )

    # ── Cotisations ───────────────────────────────────────────────────────────
    taux_cnas_sal = fields.Float(string='Taux CNAS Salarié (%)')
    taux_cnas_pat = fields.Float(string='Taux CNAS Patronal (%)')

    # ── Résultats calculés ────────────────────────────────────────────────────
    salaire_brut = fields.Float(
        string='Salaire Brut (DA)', compute='_compute_elements', store=True
    )
    montant_cotisable = fields.Float(
        string='Montant Cotisable CNAS (DA)', compute='_compute_elements', store=True
    )
    cnas_salarie = fields.Float(
        string='CNAS Salarié (DA)', compute='_compute_elements', store=True
    )
    cnas_patronal = fields.Float(
        string='CNAS Patronal (DA)', compute='_compute_elements', store=True
    )
    base_irg = fields.Float(
        string='Base IRG (DA)', compute='_compute_elements', store=True
    )
    irg = fields.Float(
        string='IRG (DA)', compute='_compute_elements', store=True
    )
    allocation_familiale = fields.Float(
        string='Allocations Familiales (DA)', compute='_compute_elements', store=True
    )
    retenue_retards = fields.Float(
        string='Retenue Retards (DA)', compute='_compute_elements', store=True
    )
    retenue_absences = fields.Float(
        string='Retenue Absences (DA)', compute='_compute_elements', store=True
    )
    total_retenues = fields.Float(
        string='Total Retenues (DA)', compute='_compute_elements', store=True
    )
    salaire_net = fields.Float(
        string='Net à Payer (DA)', compute='_compute_elements', store=True
    )
    charge_patronale = fields.Float(
        string='Charge Patronale (DA)', compute='_compute_elements', store=True
    )

    # ── Lignes de rubrique ────────────────────────────────────────────────────
    ligne_ids = fields.One2many(
        'cdc.ligne.bulletin', 'bulletin_id', string='Lignes de Rubrique'
    )

    # ── État ─────────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('calcule', 'Calculé'),
        ('valide', 'Validé'),
        ('paye', 'Payé'),
        ('annule', 'Annulé'),
    ], string='État', default='brouillon', tracking=True)

    notes = fields.Text(string='Notes / Observations')

    # ── Computed fields ───────────────────────────────────────────────────────
    @api.depends('employe_id.job_id')
    def _compute_fonction(self):
        for rec in self:
            rec.fonction = rec.employe_id.job_id.name or ''

    @api.depends(
        'salaire_base', 'taux_iep', 'salaire_poste',
        'indemnite_panier', 'indemnite_transport', 'indemnites_variables',
        'prime_responsabilite', 'prime_sujetion', 'prime_ifsp',
        'jours_ouvrables', 'jours_travailles', 'jours_absences', 'retards_heures',
        'jours_conges', 'nbre_enfants',
        'parametrage_id',
    )
    def _compute_elements(self):
        for bulletin in self:
            param = bulletin.parametrage_id
            if not param:
                bulletin.iep = bulletin.salaire_brut = bulletin.cnas_salarie = 0.0
                bulletin.cnas_patronal = bulletin.irg = bulletin.salaire_net = 0.0
                bulletin.base_irg = bulletin.charge_patronale = 0.0
                bulletin.montant_cotisable = bulletin.total_retenues = 0.0
                bulletin.allocation_familiale = 0.0
                bulletin.retenue_retards = bulletin.retenue_absences = 0.0
                continue

            sb = bulletin.salaire_base
            jo = bulletin.jours_ouvrables or param.jours_ouvrables or 26
            jt = bulletin.jours_travailles if bulletin.jours_travailles <= jo else jo
            ratio = jt / jo if jo > 0 else 1.0

            # IEP
            iep = sb * (bulletin.taux_iep / 100.0)
            bulletin.iep = iep

            # Indemnités non soumises à CNAS
            indemnites = (
                bulletin.indemnite_panier
                + bulletin.indemnite_transport
                + bulletin.indemnites_variables
            )

            # Primes
            primes = (
                bulletin.prime_responsabilite
                + bulletin.prime_sujetion
                + bulletin.prime_ifsp
            )

            # Brut
            brut = (sb + iep + primes) * ratio + indemnites
            bulletin.salaire_brut = brut

            # CNAS
            taux_sal = param.taux_cnas_salarie / 100.0
            taux_pat = param.taux_cnas_patronal / 100.0
            plafond = param.plafond_cnas
            base_cnas = (sb + iep + primes) * ratio
            if plafond and base_cnas > plafond:
                base_cnas = plafond
            bulletin.montant_cotisable = base_cnas
            cnas_sal = base_cnas * taux_sal
            cnas_pat = base_cnas * taux_pat
            bulletin.cnas_salarie = cnas_sal
            bulletin.cnas_patronal = cnas_pat

            # IRG
            base_irg = base_cnas - cnas_sal
            bulletin.base_irg = base_irg
            irg = bulletin._calcul_irg(base_irg, param)
            bulletin.irg = irg

            # Allocations Familiales
            alloc = bulletin.nbre_enfants * param.taux_allocation_familiale
            bulletin.allocation_familiale = alloc

            # Retenues Retards
            retenue_retards = 0.0
            if bulletin.retards_heures and jo > 0:
                taux_horaire = sb / (jo * 8)
                retenue_retards = taux_horaire * bulletin.retards_heures
            bulletin.retenue_retards = retenue_retards

            # Retenues Absences
            retenue_absences = 0.0
            if bulletin.jours_absences and jo > 0:
                retenue_absences = (sb / jo) * bulletin.jours_absences
            bulletin.retenue_absences = retenue_absences

            # Congés payés
            conges_payes = 0.0
            if bulletin.jours_conges and jo > 0:
                conges_payes = (sb / jo) * bulletin.jours_conges

            # Total retenues
            total_retenues = cnas_sal + irg + retenue_retards + retenue_absences
            bulletin.total_retenues = total_retenues

            # Net à Payer
            net = brut - cnas_sal - irg - retenue_retards - retenue_absences + alloc + conges_payes
            bulletin.salaire_net = net

            # Charge Patronale
            bulletin.charge_patronale = brut + cnas_pat

    def _calcul_irg(self, base_irg, param):
        if not param.taux_irg_ids:
            return 0.0
        irg = 0.0
        for tranche in param.taux_irg_ids.sorted('tranche_min'):
            lower = tranche.tranche_min
            upper = tranche.tranche_max if tranche.tranche_max > 0 else float('inf')
            taux = tranche.taux / 100.0
            deduction = tranche.deduction
            if base_irg <= lower:
                break
            if base_irg >= lower:
                montant_tranche = min(base_irg, upper) - lower
                if montant_tranche > 0:
                    irg = montant_tranche * taux - deduction
        return max(irg, 0.0)

    # ── ORM Overrides ─────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cdc.bulletin.paie'
                ) or 'Nouveau'
        return super().create(vals_list)

    @api.onchange('employe_id', 'parametrage_id')
    def _onchange_employe(self):
        if self.employe_id and self.parametrage_id:
            self.indemnite_panier = self.parametrage_id.indemnite_panier
            self.indemnite_transport = self.parametrage_id.indemnite_transport
            self.taux_cnas_sal = self.parametrage_id.taux_cnas_salarie
            self.taux_cnas_pat = self.parametrage_id.taux_cnas_patronal
            self.jours_ouvrables = self.parametrage_id.jours_ouvrables

    # ── Workflow actions ───────────────────────────────────────────────────────
    def action_calculer(self):
        for bulletin in self:
            if bulletin.state not in ('brouillon', 'calcule'):
                raise UserError(_("Seuls les bulletins en brouillon peuvent être recalculés."))
            bulletin._compute_elements()
            bulletin.state = 'calcule'
        return True

    def action_valider(self):
        for bulletin in self:
            if bulletin.state != 'calcule':
                raise UserError(_("Le bulletin doit être calculé avant validation."))
            bulletin.state = 'valide'

    def action_payer(self):
        for bulletin in self:
            if bulletin.state != 'valide':
                raise UserError(_("Le bulletin doit être validé avant paiement."))
            bulletin.state = 'paye'

    def action_annuler(self):
        for bulletin in self:
            if bulletin.state == 'paye':
                raise UserError(_("Impossible d'annuler un bulletin déjà payé."))
            bulletin.state = 'annule'

    def action_remettre_brouillon(self):
        for bulletin in self:
            if bulletin.state == 'annule':
                bulletin.state = 'brouillon'

    def action_imprimer_bulletin(self):
        return self.env.ref('cdc_paie.action_report_bulletin_paie').report_action(self)


class LigneBulletin(models.Model):
    _name = 'cdc.ligne.bulletin'
    _description = 'Ligne de Bulletin de Paie'
    _order = 'sequence, rubrique_id'

    bulletin_id = fields.Many2one(
        'cdc.bulletin.paie', string='Bulletin', ondelete='cascade'
    )
    rubrique_id = fields.Many2one(
        'cdc.rubrique.paie', string='Rubrique', required=True
    )
    name = fields.Char(related='rubrique_id.name', store=True)
    code = fields.Char(related='rubrique_id.code', store=True)
    type_rubrique = fields.Selection(related='rubrique_id.type_rubrique', store=True)
    sequence = fields.Integer(related='rubrique_id.sequence', store=True)
    montant = fields.Float(string='Montant (DA)')
    notes = fields.Char(string='Observations')