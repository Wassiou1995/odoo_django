from odoo import fields, models, api, _


class DailyProductionReport(models.Model):
    _name = 'daily.production'
    _description = 'daily production report'
    _rec_name = 'name_seq_daily_production'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    user_id = fields.Char(string='Project Manager')
    date = fields.Date(String='date')
    daily_production_lines = fields.One2many('daily.production.lines', 'project_id', string='Daily Production')
    Site = fields.Char(string='Site Address')
    name_seq_daily_production = fields.Char(string='Daily Production', required=True, copy=False, readonly=True,
                                            index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name_seq_daily_production', _('New')) == _('New'):
            vals['name_seq_daily_production'] = self.env['ir.sequence'].next_by_code('daily.production.sequence') or \
                                          _('New')
        result = super(DailyProductionReport, self).create(vals)
        return result


class DailyProductionReportLines (models.Model):
    _name = 'daily.production.lines'
    _description = 'daily production items'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    name = fields.Many2one('survey.survey', string='name', Domain=[('project_id', '=', 'project_id.id')])
    Shift = fields.Char(string='Shift')
    Weight = fields.Float(string='Weight')
    Pro_QTY = fields.Integer(string='Pro_QTY')
    Area = fields.Float(string='Area')
    Worked_Hours = fields.Integer(string='Worked_Hours')
    Rate = fields.Char(string='Rate')
    Amount = fields.Float(string='Amount')
    Remarks = fields.Text(string='Remarks')
    Status = fields.Char(string='Status')











