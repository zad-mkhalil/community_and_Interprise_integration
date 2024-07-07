from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)


class HRLeaveIntegration(models.Model):
    _inherit = 'hr.leave'

    x_external_reference = fields.Char(string="External Reference", readonly=True, unique=True,
                                       help="Unique reference for integration purposes")
    url = fields.Char(string="URL")
    db = fields.Char(string="Database Name")
    username = fields.Char(string="Username")
    password = fields.Char(string="API Key")
    is_enterprise_record = fields.Boolean(string="Enterprise Record", default=False, readonly=True)
    is_sync = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            employee_name = self.env['hr.employee'].browse(vals.get('employee_id')).name
            sequence = self.env['ir.sequence'].next_by_code('hr.leave') or '/'
            vals['x_external_reference'] = '{}-{}'.format(employee_name, sequence)
            vals['is_enterprise_record'] = False  # Mark as community record by default

        record = super(HRLeaveIntegration, self).create(vals)

        # Only perform synchronization if it's not already part of synchronization
        if not self._context.get('is_sync', False):
            self._create_leave_in_enterprise(record)

        return record

    def write(self, vals):
        if 'is_enterprise_record' in vals and vals['is_enterprise_record']:
            # If 'is_enterprise_record' is being updated to True, do not trigger update
            return super(HRLeaveIntegration, self).write(vals)

        result = super(HRLeaveIntegration, self).write(vals)

        if not self._context.get('is_sync', False):
            try:
                self.with_context(is_sync=True)._update_leave_in_enterprise()
                self.is_enterprise_record = False  # Reset the flag after update
            except Exception as e:
                _logger.error(f"Error updating leave in Enterprise: {e}")

        return result

    def unlink(self):
        if not self._context.get('is_sync', False):
            try:
                self.with_context(is_sync=True)._delete_leave_in_enterprise()
            except Exception as e:
                # Log the error and continue
                _logger.error(f"Error deleting leave in Enterprise: {e}")

        return super(HRLeaveIntegration, self).unlink()

    def _create_leave_in_enterprise(self, record):
        try:
            url = record.url
            db = record.db
            username = record.username
            password = record.password

            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

            leave_vals = {
                'employee_id': record.employee_id.id,
                'x_external_reference': record.x_external_reference,
                'holiday_status_id': record.holiday_status_id.id,
                'date_from': record.date_from,
                'date_to': record.date_to,
                'number_of_days': record.number_of_days,
                'name': record.name,
            }
            models.execute_kw(db, uid, password, 'hr.leave', 'create', [leave_vals])
        except Exception as e:
            _logger.error(f"Error creating leave in Enterprise: {e}")

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
            if enterprise_leave_id:
                leave_vals = {
                    'employee_id': self.employee_id.id,
                    'x_external_reference': self.x_external_reference,
                    'holiday_status_id': self.holiday_status_id.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'number_of_days': self.number_of_days,
                    'name': self.name,
                    'is_community_record': True
                }
                models.execute_kw(db, uid, password, 'hr.leave', 'write', [[enterprise_leave_id[0]], leave_vals])
        except Exception as e:
            _logger.error(f"Error updating leave in Enterprise: {e}")

    def _delete_leave_in_enterprise(self):
        try:
            url = self.url
            db = self.db
            username = self.username
            password = self.password

            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

            for record in self:
                enterprise_leave_id = models.execute_kw(db, uid, password, 'hr.leave', 'search',
                                                        [[['x_external_reference', '=', record.x_external_reference]]])
                if enterprise_leave_id:
                    models.execute_kw(db, uid, password, 'hr.leave', 'unlink', [enterprise_leave_id])
        except Exception as e:
            _logger.error(f"Error deleting leave in Enterprise: {e}")
