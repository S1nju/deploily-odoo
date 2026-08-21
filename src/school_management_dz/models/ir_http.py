from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        res = super()._dispatch(endpoint)
        if request and request.session.uid and request.httprequest.path not in ['/my/parent/setup', '/web/logout', '/web/login']:
            # Avoid locking out backend users
            user = request.env.user
            if user.has_group('base.group_portal') and not user.has_group('base.group_user'):
                partner = user.partner_id
                if not partner.parent_activity or not partner.mahara_participation:
                    return request.redirect('/my/parent/setup')
        return res
