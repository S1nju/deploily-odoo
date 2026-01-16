from odoo import models, fields

class HrEmployee(models.Model):
    _name = "hr.employee"
    _description = "Employee Category"
    _inherit = "hr.employee"

    in_mission = fields.Boolean(string="In Mission")
    missions_ids = fields.One2many('hr.employee.mission', 'employee_id', string='Missions')

