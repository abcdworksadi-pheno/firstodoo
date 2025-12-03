# -*- coding: utf-8 -*-
# from odoo import http


# class MonModulecicd(http.Controller):
#     @http.route('/mon_modulecicd/mon_modulecicd', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mon_modulecicd/mon_modulecicd/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mon_modulecicd.listing', {
#             'root': '/mon_modulecicd/mon_modulecicd',
#             'objects': http.request.env['mon_modulecicd.mon_modulecicd'].search([]),
#         })

#     @http.route('/mon_modulecicd/mon_modulecicd/objects/<model("mon_modulecicd.mon_modulecicd"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mon_modulecicd.object', {
#             'object': obj
#         })

