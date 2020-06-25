
from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class ConstructionEstimation (models.Model):
    _name = 'construction.estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Estimation Project Records'
    _rec_name = 'name_seq_estimation'

    project_id = fields.Many2one('project.project', string='Project')
    Mould = fields.Float(string='Mould Amount', compute='_compute_amount', required=True, track_visibility='onchange')
    Quantity = fields.Integer(string='Quantity Mould', track_visibility='onchange')
    Price = fields.Float(string='Price Mould', track_visibility='onchange')
    Production = fields.Float(string='Production Amount', compute='_compute_amount_production', required=True,
                              track_visibility='onchange')
    Row_materials = fields.Float(string='Materials Amount', track_visibility='onchange')
    Manpower = fields.Float(string='Manpower Amount', track_visibility='onchange')
    Steel_works = fields.Float(string='Steel Works Amount', track_visibility='onchange')
    Others = fields.Float(string='Others Amount', track_visibility='onchange')
    Delivery = fields.Float(string='Delivery Amount', required=True, track_visibility='onchange')
    Erection = fields.Float(string='Erection Amount', compute='_compute_amount_erection', required=True,
                            track_visibility='onchange')
    Estimated_MM = fields.Float(string='Estimated materials & Machines Amount')
    Estimated_M = fields.Float(string='Estimated Manpower ', track_visibility='onchange')
    Indirect_cost = fields.Float(string='Indirect Cost ', required=True, track_visibility='onchange')
    amount_total = fields.Float(string='Amount Total', compute='_compute_amount_total', track_visibility='onchange',
                                required=False, store=True)
    name_seq_estimation = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                                      index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('new', 'New'),
        ('department_approval', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting User Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel')], string='Stage', copy=False, default="new")

    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    Mould_percent = fields.Float(string='Mould Amount', compute='_compute_amount_percent', required=True)
    Production_percent = fields.Float(string='Production Amount', compute='_compute_amount_production_percent', required=True)
    Delivery_percent = fields.Float(string='Delivery Amount', compute='_compute_amount_delivery_percent', required=True)
    Erection_percent = fields.Float(string='Erection Amount', compute='_compute_amount_erection_percent', required=True)
    Indirect_cost_percent = fields.Float(string='Indirect Cost ', compute='_compute_amount_ic_percent')
    Mould_price = fields.Float(string='Mould Amount', compute='_compute_amount_price', required=True)
    Production_price = fields.Float(string='Production Amount', compute='_compute_amount_production_price',
                                    required=True)
    Delivery_price = fields.Float(string='Delivery Amount', compute='_compute_amount_delivery_price', required=True)
    Erection_price = fields.Float(string='Erection Amount', compute='_compute_amount_erection_price', required=True)
    Indirect_cost_price = fields.Float(string='Indirect Cost ', compute='_compute_amount_ic_price')
    Pricing_count = fields.Integer(string='Pricing', compute='get_pricing_count')
    Drawing_count = fields.Integer(string='drawing', compute='get_drawing_count')
    job_estimation_description = fields.Text('Job estimation Description')
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    pricing_count = fields.Integer(compute='get_pricing_count', string="Number of Pricings")
    active = fields.Boolean(default=True,
                help="If the active field is set to False, it will allow you to hide the estimation without removing it.")
    File = fields.Binary(string='Estimation File ', required=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company")
    confirmed_by_id = fields.Many2one('res.users', string="Confirmed By", copy=False)
    department_manager_id = fields.Many2one('res.users', string="Department Manager", copy=False)
    approved_by_id = fields.Many2one('res.users', string="Approved By", copy=False)
    rejected_by = fields.Many2one('res.users', string="Rejected By", copy=False)
    confirmed_date = fields.Date(string="Confirmed Date", readonly=True, copy=False)
    department_approval_date = fields.Date(string="Department Approval Date", readonly=True, copy=False)
    approved_date = fields.Date(string="Approved Date", readonly=True, copy=False)
    rejected_date = fields.Date(string="Rejected Date", readonly=True, copy=False)
    reason_for_requisition = fields.Text(string="Reason For Requisition")


    # Create one pricing for the projects
    @api.multi
    def open_pricing(self):
        self.ensure_one()
        return {
            'name': _('Pricing'),
            'domain': [('project_id', '=', self.project_id.id)],
            'res_model': 'construction.pricing',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.project_id.id)
        }

    #the Status of estimations ( Confirm , Approve , reject )
    @api.multi
    def confirm_estimation(self):
        res = self.write({
            'state': 'department_approval',
            'confirmed_by_id': self.env.user.id,
            'confirmed_date': datetime.now()
        })
        return res

    @api.multi
    def department_approve(self):
        res = self.write({
            'state': 'ir_approve',
            'department_manager_id': self.env.user.id,
            'department_approval_date': datetime.now()
        })
        return res

    @api.multi
    def action_cancel(self):
        res = self.write({
            'state': 'cancel',
        })
        return res

    @api.multi
    def action_reject(self):
        res = self.write({
            'state': 'cancel',
            'rejected_date': datetime.now(),
            'rejected_by': self.env.user.id
        })
        return res

    @api.multi
    def action_reset_draft(self):
        res = self.write({
                'state': 'new',
            })
        return res

    @api.multi
    def action_approve(self):
        res = self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': datetime.now()
        })
        return res

    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id.id

    @api.multi
    def open_drawing(self):
        return {
            'name': _('Drawings'),
            'domain': [('project_id', '=', 'project_id.id')],
            'view_type': 'form',
            'res_model': 'survey.survey',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    def _compute_attached_docs_count(self):
        attachment = self.env['ir.attachment']
        for estimation in self:
            estimation.doc_count = attachment.search_count([
                ('res_model', '=', 'construction.estimation'), ('res_id', '=', estimation.id)])


    # save documents for the projects
    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'construction.estimation'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="o_view_nocontent_smiling_face">
                            Documents are attached to the tasks and issues of your project.</p><p>
                            Send messages or log internal notes with attachments to link
                            documents to your project.
                        </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    def get_pricing_count(self):
        count = self.env['construction.pricing'].search_count([('project_id', '=', self.project_id.id)])
        self.pricing_count = count

    def action_confirm(self):
        for rec in self:
            rec.state = 'Confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'Done'

    #Create sequence for projects
    @api.model
    def create(self, vals):
        if vals.get('name_seq_estimation', _('New')) == _('New'):
            vals['name_seq_estimation'] = self.env['ir.sequence'].next_by_code('construction.estimation.sequence') or \
                                          _('New')
        result = super(ConstructionEstimation, self).create(vals)
        return result

    #Compute total amount
    @api.multi
    @api.depends('Mould', 'Production', 'Delivery', 'Erection', 'Indirect_cost')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = (rec.Mould + rec.Production + rec.Delivery + rec.Erection + rec.Indirect_cost)


    #Compute Mould cost
    @api.multi
    @api.depends('Quantity', 'Price')
    def _compute_amount(self):
        for rec in self:
            rec.Mould = rec.Quantity*rec.Price

    #Compute amount for department ( production  & erection & delivery )
    @api.multi
    @api.depends('Row_materials', 'Manpower', 'Steel_works', 'Others')
    def _compute_amount_production(self):
        for rec in self:
            rec.Production = rec.Row_materials + rec.Manpower + rec.Steel_works + rec.Others

    @api.multi
    @api.depends('Estimated_MM', 'Estimated_M')
    def _compute_amount_erection(self):
        for rec in self:
            rec.Erection = rec.Estimated_MM + rec.Estimated_M

    @api.multi
    @api.depends('Mould', 'amount_total')
    def _compute_amount_percent(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Mould_percent = (rec.Mould / rec.amount_total)*100

    @api.multi
    @api.depends('Production', 'amount_total')
    def _compute_amount_production_percent(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Production_percent = (rec.Production / rec.amount_total) * 100

    @api.multi
    @api.depends('Delivery', 'amount_total')
    def _compute_amount_delivery_percent(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Delivery_percent = (rec.Delivery / rec.amount_total) * 100

    @api.multi
    @api.depends('Erection', 'amount_total')
    def _compute_amount_erection_percent(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Erection_percent = (rec.Erection / rec.amount_total) * 100

    @api.multi
    @api.depends('Indirect_cost', 'amount_total')
    def _compute_amount_ic_percent(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Indirect_cost_percent = (rec.Indirect_cost / rec.amount_total) * 100

    @api.multi
    @api.depends('Mould', 'amount_total')
    def _compute_amount_price(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Mould_price = (rec.Mould / 28)

    @api.multi
    @api.depends('Production', 'amount_total')
    def _compute_amount_production_price(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Production_price = (rec.Production / 28)

    @api.multi
    @api.depends('Delivery', 'amount_total')
    def _compute_amount_delivery_price(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Delivery_price = (rec.Delivery / 28)

    @api.multi
    @api.depends('Erection', 'amount_total')
    def _compute_amount_erection_price(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Erection_price = (rec.Erection / 28)

    @api.multi
    @api.depends('Indirect_cost', 'amount_total')
    def _compute_amount_ic_price(self):
        for rec in self:
            if rec.amount_total > 0:
                rec.Indirect_cost_price = (rec.Indirect_cost / 28)


class ProjectPricing (models.Model):
    _name = 'construction.pricing'
    _description = 'Pricing & Generate BOQ '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq_pricing'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    cost_production = fields.Float(String='Cost / m² Production', required=True)
    cost_delivery = fields.Float(String='Cost / m² Delivery', required=True)
    cost_erection = fields.Float(String='Cost / m² Erection', required=True)
    UR_production = fields.Float(String='Sell Price Production', compute="_compute_UR_production", required=True)
    UR_delivery = fields.Float(String='Sell Price Delivery', compute="_compute_UR_delivery", required=True)
    UR_erection = fields.Float(String='Sell Price Erection', compute="_compute_UR_erection", required=True)
    margin = fields.Float(String='Margin', default=25)
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    name_seq_pricing = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                                    index=True, default=lambda self: _('New'))
    Drawing_count = fields.Integer(string='drawing', compute='get_drawing_count')
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the estimation without removing it.")


    @api.multi
    @api.depends('cost_production', 'margin')
    def _compute_UR_production(self):
        for rec in self:
            rec.UR_production = rec.cost_production + ((rec.margin * rec.cost_production)/100)

    @api.multi
    @api.depends('cost_delivery', 'margin')
    def _compute_UR_delivery(self):
        for rec in self:
            rec.UR_delivery = rec.cost_delivery + ((rec.margin * rec.cost_delivery) / 100)


    @api.multi
    @api.depends('cost_erection', 'margin')
    def _compute_UR_erection(self):
        for rec in self:
            rec.UR_erection = rec.cost_erection + ((rec.margin * rec.cost_erection) / 100)

    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id.id

    @api.model
    def create(self, vals):
        if vals.get('name_seq_pricing', _('New')) == _('New'):
            vals['name_seq_pricing'] = self.env['ir.sequence'].next_by_code('construction.pricing.sequence') or \
                                          _('New')
        result = super(ProjectPricing, self).create(vals)
        return result

    @api.multi
    def open_drawing(self):
        self.ensure_one()
        return {
            'name': _('Create Drawing'),
            'domain': [('project_id', '=', self.project_id.id)],
            'res_model': 'construction.drawing',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d,'default_pricing_id': %d}" % (self.project_id.id, self.id)
        }

    def get_drawing_count(self):
        count = self.env['construction.drawing'].search_count([('project_id', '=', self.project_id.id)])
        self.Drawing_count = count