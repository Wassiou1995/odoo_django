# -*- coding: utf-8 -*-
from odoo import http

# class ConstructionManagement(http.Controller):
#     @http.route('/construction_management/construction_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/construction_management/construction_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('construction_management.listing', {
#             'root': '/construction_management/construction_management',
#             'objects': http.request.env['construction_management.construction_management'].search([]),
#         })

#     @http.route('/construction_management/construction_management/objects/<model("construction_management.construction_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('construction_management.object', {
#             'object': obj
#         })