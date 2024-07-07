# -*- coding: utf-8 -*-
# from odoo import http


# class SalesComIntegPackage(http.Controller):
#     @http.route('/sales_com_integ_package/sales_com_integ_package', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_com_integ_package/sales_com_integ_package/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_com_integ_package.listing', {
#             'root': '/sales_com_integ_package/sales_com_integ_package',
#             'objects': http.request.env['sales_com_integ_package.sales_com_integ_package'].search([]),
#         })

#     @http.route('/sales_com_integ_package/sales_com_integ_package/objects/<model("sales_com_integ_package.sales_com_integ_package"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_com_integ_package.object', {
#             'object': obj
#         })
