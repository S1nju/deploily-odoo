from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    template_id = fields.Many2one(
        'hr.contract.template',
        string='Modèle de contrat'
    )

    article_ids = fields.One2many(
        'hr.contract.article',
        'contract_id',
        string='Articles',
        copy=True
    )

    def get_year_in_arabic(self):
        """Convertir l'année en texte arabe"""
        ones = ['', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة']
        tens = ['', 'عشرة', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون']
        hundreds = ['', 'مائة', 'مائتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة']

        for rec in self:
            year = rec.date_start.year if rec.date_start else 2023

            if year < 2000 or year > 2099:
                rec.year_in_arabic = str(year)
                continue

            result = 'ألفين'
            remainder = year - 2000

            if remainder == 0:
                rec.year_in_arabic = result
                continue

            result += ' و'

            h = remainder // 100
            if h:
                result += hundreds[h]
                remainder %= 100
                if remainder:
                    result += ' و'

            if remainder >= 10:
                t = remainder // 10
                o = remainder % 10
                if o:
                    result += ones[o] + ' و' + tens[t]
                else:
                    result += tens[t]
            elif remainder:
                result += ones[remainder]

            rec.year_in_arabic = result

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Copier les articles du modèle vers le contrat"""
        for rec in self:
            if rec.template_id:
                rec.article_ids = [(5, 0, 0)]

                rec.article_ids = [
                    (0, 0, {
                        'name': a.name,
                        'content': a.content,
                        'sequence': a.sequence,
                    })
                    for a in rec.template_id.article_ids.sorted('sequence')
                ]