from odoo import http, _
from odoo.http import request

class SchoolPortal(http.Controller):

    @http.route(['/my/parent/setup'], type='http', auth='user', website=True)
    def parent_setup(self, **post):
        partner = request.env.user.partner_id
        if request.httprequest.method == 'POST':
            partner.sudo().write({
                'parent_activity': post.get('parent_activity'),
                'mahara_participation': post.get('mahara_participation'),
            })
            return request.redirect('/services')
        
        return request.render('school_management_dz.parent_setup_form', {
            'partner': partner,
        })

    @http.route(['/services'], type='http', auth='public', website=True)
    def services_catalog(self, **kw):
        # List categories
        categories = request.env['school.service.category'].sudo().search([])
        return request.render('school_management_dz.services_catalog', {
            'categories': categories,
        })
        
    @http.route(['/services/<model("school.service.category"):category>'], type='http', auth='public', website=True)
    def services_category(self, category, **kw):
        return request.render('school_management_dz.services_category', {
            'category': category,
        })
        
    @http.route(['/course/<model("school.course"):course>'], type='http', auth='public', website=True)
    def course_details(self, course, **kw):
        return request.render('school_management_dz.course_details', {
            'course': course,
            'main_object': course,
        })

    @http.route(['/course/<model("school.course"):course>/register'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def course_register(self, course, **kw):
        if request.httprequest.method == 'GET':
            return request.render('school_management_dz.course_register_form', {
                'course': course,
            })
            
        parent = request.env.user.partner_id
        student_name = kw.get('student_name')
        test_answer = kw.get('test_answer', '')
        
        student = request.env['school.student'].sudo().create({
            'name': student_name, 
            'parent_id': parent.id
        })
        
        stage = request.env['crm.stage'].sudo().search([('name', '=', 'استشارة مجانية')], limit=1)
        lead_vals = {
            'name': f"{student_name} - {course.name}",
            'partner_id': parent.id,
            'student_id': student.id,
            'description': f"Registration Request.\nStudent: {student_name}\nTest Answer Form: {test_answer}",
        }
        if stage:
            lead_vals['stage_id'] = stage.id
            
        lead = request.env['crm.lead'].sudo().create(lead_vals)
        
        request.env['school.registration'].sudo().create({
            'parent_id': parent.id,
            'course_id': course.id,
            'student_ids': [(4, student.id)],
            'crm_lead_id': lead.id,
        })
        
        return request.render('school_management_dz.registration_success', {
            'student': student,
            'course': course,
        })
