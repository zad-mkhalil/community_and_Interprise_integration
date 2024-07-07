from odoo import models, fields, api
import xmlrpc.client
import logging


class SaleOrderIntegration(models.Model):
    _inherit = 'sale.order'
    url = fields.Char(string="URL")
    db = fields.Char(string="Database name")
    username = fields.Char(string="Username")
    password = fields.Char(string="Api Key")
    _is_sync = fields.Boolean(string="Is Synchronization", default=False)




    def write(self,vals):
        # Call the original write method
        result = super(SaleOrderIntegration, self).write(vals)
        if not self._context.get('is_sync', False):
            vals['_is_sync'] = True
            # Update sales order in the Enterprise instance
        if not self._context.get('is_sync', False):
          self._update_sales_order_in_enterprise(
                self.url, self.db, self.username, self.password
            )
        return result


    def _update_sales_order_in_enterprise(self, url, db, username, password):
        # Define connection parameters

        # Connect to the Enterprise instance
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Find the corresponding sales order in the Enterprise instance
        enterprise_order_id = models.execute_kw(db, uid, password, 'sale.order', 'search',
                                                [[['name', '=', self.name]]])
        if not enterprise_order_id:
            # _logger.warning('Sales order %s does not exist in the Enterprise instance', self.name)
            print('Sales order %s does not exist in the Enterprise instance')
            return

        sales_order_vals = {
            'partner_id': self.partner_id.id,
            'state': self.state,
            'order_line': []
        }
        for line in self.order_line:
            # Check if the order line exists in the Enterprise instance
            enterprise_order_line_id = models.execute_kw(db, uid, password, 'sale.order.line', 'search',
                                                         [[['product_id', '=', line.product_id.id],
                                                          ['order_id', '=', enterprise_order_id[0]]]])
            if enterprise_order_line_id:
                # Update the existing order line
                sales_order_vals['order_line'].append((1, enterprise_order_line_id[0], {
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,

                }))

            else:

                # Create a new order line
                sales_order_vals['order_line'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                }))
        models.execute_kw(db, uid, password, 'sale.order', 'write',
                          [[enterprise_order_id[0]], sales_order_vals])

