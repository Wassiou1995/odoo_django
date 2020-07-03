from odoo import fields, models, api, _


class DailyDeliveryReport(models.Model):
    _name = 'daily.delivery'
    _description = 'daily delivery report'
    _rec_name = 'name_seq_daily_delivery'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    user_id = fields.Char(string='Project Manager')
    date = fields.Date(String='date')
    daily_delivery_lines = fields.One2many('daily.delivery.lines', 'project_id', string='Daily Delivery Report')
    Site = fields.Char(string='Site Address')
    name_seq_daily_delivery = fields.Char(string='Daily Delivery', required=True, copy=False, readonly=True,
                                          index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name_seq_daily_delivery', _('New')) == _('New'):
            vals['name_seq_daily_delivery'] = self.env['ir.sequence'].next_by_code('daily.delivery.sequence') or \
                                          _('New')
        result = super(DailyDeliveryReport, self).create(vals)
        return result


class DailyDeliveryReportLines (models.Model):
    _name = 'daily.delivery.lines'
    _description = 'daily delivery items'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    name = fields.Char(string='name')
    Area = fields.Float(string='Area (m²)')
    Total_area = fields.Float(string='Total Area (m²)')
    delivery_note = fields.Text(string='Delivery Note')
    vehicle_no = fields.Integer(string='Vehicle No')
    Driver_name = fields.Char(string='Driver Name')
    Distance = fields.Float(string='Distance (Km)')
    Km_rate = fields.Float(string='Km Rate')
    Amount = fields.Float(string='Amount')
    Remarks = fields.Text(string='Remarks')

