from odoo import models, fields
from odoo import api


class HrPromotion(models.Model):
    _name = 'hr.promotion'
    _description = 'Employee Promotion'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    old_position = fields.Many2one('hr.job', string="Old Position", required=True)
    new_position = fields.Many2one('hr.job', string="New Position", required=True)
    promotion_date = fields.Date(string="Promotion Date", required=True)
    old_salary = fields.Float(string="Old Salary")
    new_salary = fields.Float(string="New Salary")
    reason = fields.Text(string="Reason for Promotion")
    notes = fields.Text(string="Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ], string="State", default='draft')

    @api.model
    def _check_can_transition(self):
        return True

    def action_approve(self):
        """Approve the promotion."""
        for rec in self:
            # set state
            rec.state = 'approved'
            # update employee job
            if rec.new_position:
                rec.employee_id.job_id = rec.new_position
            # update employee contracts' wage if new_salary provided
            if rec.new_salary:
                contracts = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)])
                if contracts:
                    contracts.write({'wage': rec.new_salary})

    def action_reject(self):
        """Reject the promotion."""
        for rec in self:
            rec.state = 'rejected'

    def action_done(self):
        """Mark the promotion as done."""
        for rec in self:
            rec.state = 'done'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Populate old position and old salary from the employee when selected."""
        for rec in self:
            if rec.employee_id:
                rec.old_position = rec.employee_id.job_id or False
                # get latest contract wage if any
                contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], order='date_start desc', limit=1)
                if contract:
                    try:
                        rec.old_salary = contract.wage or 0.0
                    except Exception:
                        rec.old_salary = 0.0
                else:
                    rec.old_salary = 0.0
