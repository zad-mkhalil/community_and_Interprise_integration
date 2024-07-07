from odoo import models, fields

class HRIntegrationConfig(models.Model):
    _inherit = 'res.config.settings'
    _name = 'integration.config'
    _description = 'Integration Configuration'

    url = fields.Char(string="URL", required=True)
    db = fields.Char(string="Database Name", required=True)
    username = fields.Char(string="Username", required=True)
    password = fields.Char(string="API Key", required=True)


