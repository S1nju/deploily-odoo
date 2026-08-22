from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        res = super()._dispatch(endpoint)
        if request and request.session.uid:
            path = request.httprequest.path
            
            # Avoid intercepting static assets, web APIs, and the setup page itself
            if not path.startswith(('/web/', '/website/', '/my/parent/setup')):
                # Ensure they are normal portal users (not internal staff)
                user = request.env.user
                if user and user.has_group('base.group_portal') and not user.has_group('base.group_user'):
                    partner = user.partner_id
                    # If they are missing mandatory data, redirect them
                    if not partner.parent_activity or not partner.mahara_participation:
                        return request.redirect('/my/parent/setup')
        return res
