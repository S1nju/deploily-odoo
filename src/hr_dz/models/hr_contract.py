from odoo import models, fields,api
class HrContract(models.Model):
    _inherit = 'hr.contract'

    template_id = fields.Many2one('hr.contract.template', string='Contract Template')
    article_ids = fields.One2many('hr.contract.article', 'contract_id', string='Articles', copy=True)

    def get_year_in_arabic(self):
        """Convert year to Arabic words"""
        year = self.date_start.year if self.date_start else 2023
        
        # Arabic number words
        ones = ['', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة']
        tens = ['', 'عشر', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون']
        hundreds = ['', 'مائة', 'مائتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة']
        
        if year < 2000 or year > 2099:
            return str(year)
        
        # For years 2000-2099
        result = 'ألفين'
        
        remainder = year - 2000
        if remainder == 0:
            return result
        
        result += ' و'
        
        # Get hundreds digit
        h = remainder // 100
        if h > 0:
            result += hundreds[h]
            remainder = remainder % 100
            if remainder > 0:
                result += ' و'
        
        # Get tens and ones
        if remainder >= 10:
            t = remainder // 10
            o = remainder % 10
            if o > 0:
                result += ones[o] + ' و' + tens[t]
            else:
                result += tens[t]
        elif remainder > 0:
            result += ones[remainder]
        
        return result

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """When a template is selected, copy its articles into this contract."""
        for rec in self:
            if rec.template_id:
                # remove existing contract articles (only in-memory)
                rec.article_ids = [(5, 0, 0)]
                vals = []
                for art in rec.template_id.article_ids.sorted(key=lambda r: r.sequence):
                    vals.append((0, 0, {
                        'name': art.name,
                        'content': art.content,
                        'sequence': art.sequence,
                    }))
                if vals:
                    rec.article_ids = vals