from odoo import fields, models, api, _


class DailySiteReport(models.Model):
    _name = 'daily.site'
    _description = 'daily site report'
    _rec_name = 'name_seq_daily_site'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    user_id = fields.Many2one('res.users', string='Project Manager')
    date = fields.Date(String='date')
    daily_site_lines = fields.One2many('daily.site.lines', 'project_id', string='Daily Site Line')
    daily_material_request_lines = fields.One2many('daily.material.request.lines', 'project_id', string='Material Request')
    daily_panel_request_lines = fields.One2many('daily.panel.request.lines', 'project_id', string='Panel Request')
    Site = fields.Char(string='Site Address')
    name_seq_daily_site = fields.Char(string='Daily Site', required=True, copy=False, readonly=True,
                                      index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name_seq_daily_site', _('New')) == _('New'):
            vals['name_seq_daily_site'] = self.env['ir.sequence'].next_by_code('daily.site.sequence') or \
                                          _('New')
        result = super(DailySiteReport, self).create(vals)
        return result


class DailySiteReportLines (models.Model):
    _name = 'daily.site.lines'
    _description = 'daily site items'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    name = fields.Char(string='name')
    Quantity = fields.Float(string='Qty')
    Manpower_id = fields.Integer(string='Manpower ID')
    Manpower_name = fields.Many2one('hr.employee', string='Manpower Name')
    Trade = fields.Integer(string='Trade')
    Nb_Hours = fields.Float(string='Nb Hours')
    Rate = fields.Char(string='Rate')
    Amount = fields.Float(string='Amount')
    Remarks = fields.Text(string='Remarks')


class DailyMaterialRequestLines (models.Model):
    _name = 'daily.material.request.lines'
    _description = 'daily site items'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    Material_name = fields.Char(string='Material Name')
    Unit = fields.Float(string='Unit')
    Quantity = fields.Integer(string='Quantity')
    Hours = fields.Char(string='Hours')
    Rate = fields.Char(string='Rate')
    Amount = fields.Float(string='Amount')
    Remarks = fields.Text(string='Remarks')


class DailyPanelRequestLines (models.Model):
    _name = 'daily.panel.request.lines'
    _description = 'daily site items'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    Panel_name = fields.Char(string='Panel Name')
    Unit = fields.Float(string='Unit')
    Quantity = fields.Integer(string='Quantity')
    Hours = fields.Char(string='Hours')
    Rate = fields.Char(string='Rate')
    Amount = fields.Float(string='Amount')
    Remarks = fields.Text(string='Remarks')








