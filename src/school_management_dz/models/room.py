from odoo import models, fields

class SchoolRoom(models.Model):
    _name = 'school.room'
    _description = 'Classroom'

    name = fields.Char('Room Name', required=True)
    center_id = fields.Many2one('school.center', 'Center', required=True, ondelete='cascade')
    capacity = fields.Integer('Capacity')
    
    session_ids = fields.One2many('school.course.session', 'room_id', 'Sessions')
