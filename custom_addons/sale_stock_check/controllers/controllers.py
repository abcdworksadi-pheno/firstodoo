# -*- coding: utf-8 -*-
# from odoo import http


# class SaleStockCheck(http.Controller):
#     @http.route('/sale_stock_check/sale_stock_check', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_stock_check/sale_stock_check/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_stock_check.listing', {
#             'root': '/sale_stock_check/sale_stock_check',
#             'objects': http.request.env['sale_stock_check.sale_stock_check'].search([]),
#         })

#     @http.route('/sale_stock_check/sale_stock_check/objects/<model("sale_stock_check.sale_stock_check"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_stock_check.object', {
#             'object': obj
#         })

