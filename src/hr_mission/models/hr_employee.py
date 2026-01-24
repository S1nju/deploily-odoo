from odoo import models, fields, api
from datetime import datetime

class HrEmployee(models.Model):
    _name = "hr.employee"
    _description = "Employee Category"
    _inherit = "hr.employee"

    in_mission = fields.Boolean(string="In Mission", compute='_compute_in_mission', store=True)
    missions_ids = fields.One2many('hr.mession', 'employee_id', string='Missions')

    @api.depends('missions_ids.state', 'missions_ids.mission_start_date', 'missions_ids.mission_end_date')
    def _compute_in_mission(self):
        """Check if employee is currently in an active/approved mission"""
        today = datetime.now().date()
        for employee in self:
            is_in_mission = False
            for mission in employee.missions_ids:
                if mission.state == 'approved':
                    mission_start = mission.mission_start_date.date() if hasattr(mission.mission_start_date, 'date') else mission.mission_start_date
                    mission_end = mission.mission_end_date.date() if hasattr(mission.mission_end_date, 'date') else mission.mission_end_date
                    if mission_start <= today <= mission_end:
                        is_in_mission = True
                        break
            employee.in_mission = is_in_mission

    def action_open_missions(self):
        """Open missions view filtered for this employee"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.mession',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
            'name': f'Missions for {self.name}',
        }
