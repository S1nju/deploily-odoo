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
        
        # Check if existing student or new
        existing_id = kw.get('existing_student_id')
        student = False
        student_name = "Existing Student"
        
        if existing_id and existing_id != 'new':
            student = request.env['school.student'].sudo().browse(int(existing_id))
            student_name = student.name
        else:
            student_name = kw.get('student_name', 'New Student')
            # Build student fields for a new record
            student_vals = {
                'name': student_name,
                'parent_id': parent.id
            }
            
            # File upload processing
            grades_file = kw.get('student_grades_file')
            if grades_file and hasattr(grades_file, 'read'):
                import base64
                student_vals['grades_file'] = base64.b64encode(grades_file.read())
                student_vals['grades_filename'] = grades_file.filename
            
            for key, val in kw.items():
                if key.startswith('student_') and key not in ['student_name', 'student_grades_file']:
                    field_name = key.replace('student_', '')
                    student_vals[field_name] = val
                    
            student = request.env['school.student'].sudo().create(student_vals)
        
        # Dynamically build test answers
        answers_str = []
        for key, val in kw.items():
            if key.startswith('question_'):
                q_id = int(key.replace('question_', ''))
                q = request.env['school.course.test.question'].sudo().browse(q_id)
                if q.exists():
                    answers_str.append(f"Q: {q.name}\nA: {val}")
                    
        formatted_answers = "\n\n".join(answers_str)
        
        stage = request.env['crm.stage'].sudo().search([('name', '=', 'استشارة مجانية')], limit=1)
        lead_vals = {
            'name': f"{student_name} - {course.name}",
            'partner_id': parent.id,
            'student_id': student.id,
            'description': f"Registration Request.\nStudent: {student_name}\n\n=== Test Answers ===\n{formatted_answers}",
        }
        if stage:
            lead_vals['stage_id'] = stage.id
            
        lead = request.env['crm.lead'].sudo().create(lead_vals)
        
        request.env['school.registration'].sudo().create({
            'parent_id': parent.id,
            'course_id': course.id,
            'student_ids': [(4, student.id)],
            'crm_lead_id': lead.id,
            'test_answers': formatted_answers,
        })
        
        return request.render('school_management_dz.registration_success', {
            'student': student,
            'course': course,
        })

    @http.route(['/my/students'], type='http', auth="user", website=True)
    def portal_my_students(self, **kw):
        parent = request.env.user.partner_id
        paid_regs = request.env['school.registration'].sudo().search([
            ('parent_id', '=', parent.id),
            ('state', '=', 'paid')
        ])
        
        if not paid_regs:
            # Prevent access if no paid registrations exist
            return request.render('school_management_dz.portal_blocked_unpaid', {})
            
        students = parent.student_ids
        return request.render('school_management_dz.portal_my_students', {
            'students': students,
        })

    @http.route(['/my/students/<model("school.student"):student>'], type='http', auth="user", website=True)
    def portal_my_student_detail(self, student, **kw):
        parent = request.env.user.partner_id
        if student.parent_id.id != parent.id:
            return request.render('website.page_404')
            
        paid_regs = request.env['school.registration'].sudo().search([
            ('parent_id', '=', parent.id),
            ('state', '=', 'paid')
        ])
        
        if not paid_regs:
            return request.render('school_management_dz.portal_blocked_unpaid', {})

        registrations = request.env['school.registration'].sudo().search([
            ('parent_id', '=', parent.id),
            ('student_ids', 'in', student.ids),
            ('state', 'in', ['registered', 'paid'])
        ])

        return request.render('school_management_dz.portal_my_student_detail', {
            'student': student,
            'registrations': registrations,
        })
