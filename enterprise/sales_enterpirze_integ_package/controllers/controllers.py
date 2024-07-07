# -*- coding: utf-8 -*-
# from odoo import http


# class SalesEnterpirzeIntegPackage(http.Controller):
#     @http.route('/sales_enterpirze_integ_package/sales_enterpirze_integ_package', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_enterpirze_integ_package/sales_enterpirze_integ_package/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_enterpirze_integ_package.listing', {
#             'root': '/sales_enterpirze_integ_package/sales_enterpirze_integ_package',
#             'objects': http.request.env['sales_enterpirze_integ_package.sales_enterpirze_integ_package'].search([]),
#         })

#     @http.route('/sales_enterpirze_integ_package/sales_enterpirze_integ_package/objects/<model("sales_enterpirze_integ_package.sales_enterpirze_integ_package"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_enterpirze_integ_package.object', {
#             'object': obj
#         })
