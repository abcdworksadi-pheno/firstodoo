from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    x_section_code = fields.Char(
        string="Code Customer",
        help="Code personnalisé pour les sections"
    )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_section_code = fields.Char(
        string="Code Customer",
        help="Code personnalisé pour les sections"
    )
