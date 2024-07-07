from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)
class HRLeaveIntegration(models.Model):
    _inherit = 'hr.leave'

    x_external_reference = fields.Char(string="External Reference", unique=True,
                                       help="Unique reference for integration purposes")
    url = fields.Char(string="URL")
    db = fields.Char(string="Database name")
    username = fields.Char(string="Username")
    password = fields.Char(string="Api Key")
    is_community_record = fields.Boolean(string="Community Record", default=False, readonly=True)
    is_sync=fields.Boolean(default=False)

    def write(self, vals):
        result = super(HRLeaveIntegration, self).write(vals)
        if not self._context.get('is_sync', False):
            if 'is_enterprise_record' in vals and vals.get('is_enterprise_record'):
                print('55555555555555')
                return result
            else:
                try:
                    print('55555555555555')
                    self.with_context(is_sync=True)._update_leave_in_enterprise()
                    self.is_enterprise_record = False  # Reset the flag after update
                except Exception as e:
                    _logger.error(f"Error updating leave in Enterprise: {e}")
        return result

    def _update_leave_in_enterprise(self):
        try:
            url = self.url
            db = self.db
            username = self.username
            password = self.password

            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

            enterprise_leave_id = models.execute_kw(db, uid, password, 'hr.leave', 'search',
                                                    [[['x_external_reference', '=', self.x_external_reference]]])
            if not enterprise_leave_id:
                return

            leave_vals = {
                'employee_id': self.employee_id.id,
                'x_external_reference': self.x_external_reference,
                'holiday_status_id': self.holiday_status_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'number_of_days': self.number_of_days,
                'name': self.name,
                'state': self.state,
                'is_enterprise_record': True,
            }
            models.execute_kw(db, uid, password, 'hr.leave', 'write', [[enterprise_leave_id[0]], leave_vals])
            print('4444444444444444')
        except Exception as e:
            _logger.error(f"Error updating leave in Enterprise: {e}")
