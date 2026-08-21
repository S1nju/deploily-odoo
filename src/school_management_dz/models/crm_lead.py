from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    school_registration_ids = fields.One2many('school.registration', 'crm_lead_id', 'Registrations')
    student_id = fields.Many2one('school.student', 'Student')
    
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if 'stage_id' in vals:
            for lead in self:
                # Trigger paid state based on the specific 'Paid' stage
                if lead.stage_id.name and lead.stage_id.name.lower() == 'paid':
                    lead.school_registration_ids.write({'state': 'paid'})
        return res
