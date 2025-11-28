# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeMood(http.Controller):
#     @http.route('/employee_mood/employee_mood', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_mood/employee_mood/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_mood.listing', {
#             'root': '/employee_mood/employee_mood',
#             'objects': http.request.env['employee_mood.employee_mood'].search([]),
#         })

#     @http.route('/employee_mood/employee_mood/objects/<model("employee_mood.employee_mood"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_mood.object', {
#             'object': obj
#         })

