# -*- coding: utf-8 -*-
# from odoo import http


# class SectionCustom(http.Controller):
#     @http.route('/section_custom/section_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/section_custom/section_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('section_custom.listing', {
#             'root': '/section_custom/section_custom',
#             'objects': http.request.env['section_custom.section_custom'].search([]),
#         })

#     @http.route('/section_custom/section_custom/objects/<model("section_custom.section_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('section_custom.object', {
#             'object': obj
#         })

