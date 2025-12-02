# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class sale_stock_check(models.Model):
#     _name = 'sale_stock_check.sale_stock_check'
#     _description = 'sale_stock_check.sale_stock_check'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

from odoo import models, _
from odoo.exceptions import UserError

class sale_stock_check(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            for line in order.order_line:
                product = line.product_id
                qty_ordered = line.product_uom_qty
                qty_available = product.qty_available  # ou product.free_qty selon ton besoin

                if qty_ordered > qty_available:
                    raise UserError(_(
                        "hello sir Stock insuffisant pour le produit '%s'.\n"
                        "Demandé : %s\nDisponible : %s"
                    ) % (product.display_name, qty_ordered, qty_available))

        return super(sale_stock_check, self).action_confirm()
