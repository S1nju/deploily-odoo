from odoo import models, fields


class HrEducation(models.Model):
    _name = 'hr.education'
    _description = 'Diplômes et Formations'

    employee_id = fields.Many2one('hr.employee', string="Salarié")
    diploma_type = fields.Selection([
        ('bac', 'Baccalauréat'),
        ('licence', 'Licence'),
        ('master', 'Master'),
        ('doctorat', 'Doctorat'),
        ('certif', 'Certification Professionnelle')
    ], string="Type de diplôme")
    subject = fields.Char(string="Spécialité / Filière")
    finish_date = fields.Date(string="Date d'obtention")
    state = fields.Selection([
        ('ongoing', 'En cours'),
        ('completed', 'Terminé')
    ], string="État")
    attachment = fields.Binary(string="Copie du Diplôme")
