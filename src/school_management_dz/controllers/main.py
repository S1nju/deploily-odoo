from odoo import http, _
from odoo.http import request

class SchoolPortal(http.Controller):

    @http.route(['/my/parent/setup'], type='http', auth='user', website=True)
    def parent_setup(self, **post):
        partner = request.env.user.partner_id
        if request.httprequest.method == 'POST':
            # Create Full Name string if both are provided
            fname = post.get('custom_first_name', '')
            lname = post.get('custom_last_name', '')
            full_name = f"{fname} {lname}".strip()
            
            update_vals = {
                'parent_activity': post.get('parent_activity'),
                'mahara_participation': post.get('mahara_participation'),
                
                'custom_first_name': fname,
                'custom_last_name': lname,
                'father_name': post.get('father_name'),
                
                'phone': post.get('phone'),
                'mobile': post.get('mobile'),
                'email': post.get('email'),
                
                'is_whatsapp': 'on' in post.get('is_whatsapp', ''),
                'is_telegram': 'on' in post.get('is_telegram', ''),
                'is_viber': 'on' in post.get('is_viber', ''),
                
                'wilaya_name': post.get('wilaya_name'),
                'neighborhood_name': post.get('neighborhood_name'),
            }
            if full_name:
                update_vals['name'] = full_name
                
            partner.sudo().write(update_vals)
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
        
        if existing_id == 'self':
            student_name = parent.name
            student_vals = {}
            student = request.env['school.student'].sudo().search([('parent_id', '=', parent.id), ('name', '=', parent.name)], limit=1)
            if not student:
                student_vals = {'name': parent.name, 'parent_id': parent.id, 'relationship': 'self'}
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
        elif existing_id and existing_id != 'new':
            student = request.env['school.student'].sudo().browse(int(existing_id))
            student_name = student.name
            student_vals = {}
        else:
            fname = kw.get('student_custom_first_name', '')
            lname = kw.get('student_custom_last_name', '')
            full_name = f"{fname} {lname}".strip() or kw.get('student_name', 'New Student')
            student_name = full_name
            
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
        
        # Format student info if any
        student_info_str = ""
        if student_vals:
            lines = [f"{k}: {v}" for k, v in student_vals.items() if k not in ('grades_file', 'grades_filename')]
            student_info_str = "\n".join(lines)
            
        request.env['school.registration'].sudo().create({
            'parent_id': parent.id,
            'course_id': course.id,
            'student_ids': [(4, student.id)],
            'crm_lead_id': lead.id,
            'test_answers': formatted_answers,
            'student_info': student_info_str,
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

    @http.route(['/my/students/<model("school.student"):student>/course/<model("school.registration"):registration>'], type='http', auth="user", website=True)
    def portal_my_student_course_detail(self, student, registration, **kw):
        parent = request.env.user.partner_id

        if student.parent_id.id != parent.id:
            return request.render('website.page_404')
            
        if registration.parent_id.id != parent.id or student.id not in registration.student_ids.ids:
            return request.render('website.page_404')

        paid_regs = request.env['school.registration'].sudo().search([
            ('parent_id', '=', parent.id),
            ('state', '=', 'paid')
        ])

        if not paid_regs:
            return request.render('school_management_dz.portal_blocked_unpaid', {})

        return request.render('school_management_dz.portal_student_course_detail', {
            'student': student,
            'registration': registration,
        })

    @http.route(['/school/attendance/scanner'], type='http', auth="user", website=True)
    def scanner_view(self, **kw):
        user = request.env.user
        session_id = kw.get('session_id')
        session = None
        courses = request.env['school.course'].sudo().search([])
        
        if session_id:
            session = request.env['school.course.session'].sudo().browse(int(session_id))
            courses = session.course_id
        elif user.has_group('school_management_dz.group_school_tutor'):
            courses = request.env['school.course'].sudo().search([('tutor_id.user_id', '=', user.id)])
            
        return request.render('school_management_dz.attendance_scanner', {
            'courses': courses,
            'session': session,
        })
        
    @http.route(['/school/attendance/scan_process'], type='json', auth="user")
    def scanner_process(self, barcode, course_id, session_id=None, **kw):
        from odoo import fields
        # find student 
        student = request.env['school.student'].sudo().search([('qr_code', '=', barcode)], limit=1)
        if not student:
            return {'error': 'Student not found.'}
            
        today = fields.Date.context_today(request.env.user)
        domain = [('student_id', '=', student.id)]
        
        if session_id:
            domain.append(('session_id', '=', int(session_id)))
            session = request.env['school.course.session'].sudo().browse(int(session_id))
            course_id = session.course_id.id
            date = session.date or today
        else:
            domain.append(('course_id', '=', int(course_id)))
            domain.append(('date', '=', today))
            date = today
            
        att = request.env['school.attendance'].sudo().search(domain, limit=1)
        
        if att:
            if att.state == 'present':
                return {'success': f'{student.name} is already marked Present.'}
            else:
                att.sudo().write({'state': 'present'})
                return {'success': f'{student.name} updated to Present.'}
                
        request.env['school.attendance'].sudo().create({
            'student_id': student.id,
            'course_id': int(course_id),
            'session_id': int(session_id) if session_id else False,
            'date': date,
            'state': 'present',
        })
        return {'success': f'{student.name} marked Present successfully!'}
