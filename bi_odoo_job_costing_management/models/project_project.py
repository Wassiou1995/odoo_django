# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    name_seq_project = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                                   index=True, default='New')
    pricing_count = fields.Integer(compute='get_pricing_count', string="Number of Pricings")
    issue_count = fields.Integer(compute='_compute_issue_count', string="Issues")
    issue_ids = fields.One2many('project.issue', 'project_id', string="Issues", domain=['|', ('stage_id.fold', '=', False), ('stage_id', '=', False)])
    issue_needaction_count = fields.Integer(compute="_issue_needaction_count", string="Issues")
    job_order_count = fields.Integer('Job Order', compute='_get_job_order_count')
    purchase_order_line_count = fields.Integer('Purchase Order', compute='_get_purchase_order_line_count')
    purchase_order_count = fields.Integer('Purchase Order',compute='_get_purchase_count')
    project_id = fields.One2many('purchase.order','project_id')
    purchase_id = fields.One2many('purchase.order.line','order_id')

    #compute the total real cost of the project & the total estimated cost
    total_cost = fields.Float("Total Cost" , compute = "_compute_total_cost" , default=0.0)
    total_estimated_cost = fields.Float("Total Estimated Cost" , compute = "_compute_total_estimated_cost" , default=0.0)
    Drawing_count = fields.Integer(string='drawing', compute='get_drawing_count')
    Estimation_count = fields.Integer(string='estimation', compute='get_estimation_count')

    #Selling price and profit of the project
    selling_price = fields.Float("Selling Price" , compute = "_compute_selling_price" , default=0.0)
    total_production = fields.Float("Total Production" , compute = "_compute_total_production" , default=0.0)
    total_delivery = fields.Float("Total Delivery" , compute = "_compute_total_delivery" , default=0.0)
    total_erection = fields.Float("Total Erection" , compute = "_compute_total_erection" , default=0.0)
    profit = fields.Float("profit" , compute = "_compute_profit" , default=0.0)


    #Create sequence for estimation
    @api.model
    def create(self, vals):
        if vals.get('name_seq_project', _('New')) == _('New'):
            vals['name_seq_project'] = self.env['ir.sequence'].next_by_code('project.sequence') or _('New')
        result = super(Project, self).create(vals)
        return result

    def get_pricing_count(self):
        count = self.env['construction.pricing'].search_count([('project_id', '=', self.id)])
        self.pricing_count = count


    #open the pricing sheet
    @api.multi
    def open_pricing(self):
        self.ensure_one()
        return {
            'name': _('Pricing'),
            'domain': [('project_id', '=', self.id)],
            'res_model': 'construction.pricing',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }

    # open the drawing
    @api.multi
    def open_drawing(self):
        self.ensure_one()
        return {
            'name': _('Drawings'),
            'domain': [('project_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'construction.drawing',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_project_id': %d}" % (self.id)
        }

    # open the estimation button
    @api.multi
    def open_estimation(self):
        self.ensure_one()
        return {
            'name': _('Estimations'),
            'domain': [('project_id', '=', self.id)],
            'res_model': 'construction.estimation',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_project_id': %d}" % (self.id)
        }

    def get_estimation_count(self):
        count = self.env['construction.estimation'].search_count([('project_id', '=', self.id)])
        self.Estimation_count = count

    def get_drawing_count(self):
        count = self.env['construction.drawing'].search_count([('project_id', '=', self.id)])
        self.Drawing_count = count


    #compute the profit in the project
    @api.multi
    @api.depends('total_cost', 'selling_price')
    def _compute_profit(self):
        for rec in self:
            rec.profit = (rec.selling_price - rec.total_cost)

    @api.multi
    def _get_purchase_count(self):
        count = 0.0
        for job_cost_sheet in self:
            project_ids = self.env['job.cost.sheet'].search([('project_id', '=', job_cost_sheet.id)])
            for purchase in project_ids:
                purchase_line_ids = self.env['purchase.order.line'].search([('job_cost_sheet_id', '=', purchase.id)])
                for purchase in purchase_line_ids:
                    purchase_ids = self.env['purchase.order'].search([('id', 'in', purchase.order_id.ids)])
                    count = count + len(purchase_ids)
            job_cost_sheet.purchase_order_count = count
        return True


    #Calculate the total cost & the total estimated cost all estimations & cost sheet for the same project
    def _compute_total_cost(self):
        for project in self:
            project.total_cost=0.0
            cost_sheet = self.env['job.cost.sheet'].search([('project_id','=',project.id)])
            for sheet in cost_sheet:
                project.total_cost += sheet.total_cost

    def _compute_total_estimated_cost(self):
        for project in self:
            project.total_estimated_cost = 0.0
            cost_sheet = self.env['construction.estimation'].search([('project_id', '=', project.id)])
            for sheet in cost_sheet:
                project.total_estimated_cost += sheet.amount_total


    #computing the selling price of all drawings in the project
    def _compute_selling_price(self):
        for project in self:
            project.selling_price = 0.0
            x = self.env['construction.drawing'].search([('project_id', '=', project.id)])
            for sheet in x:
                project.selling_price += sheet.total_drawing

    #computing the production amount of all drawings in the project
    def _compute_total_production(self):
        for project in self:
            project.total_production = 0.0
            x = self.env['construction.drawing'].search([('project_id', '=', project.id)])
            for sheet in x:
                project.total_production += sheet.total_prod

    #computing the delivery amount of all drawings in the project
    def _compute_total_delivery(self):
        for project in self:
            project.total_delivery = 0.0
            x = self.env['construction.drawing'].search([('project_id', '=', project.id)])
            for sheet in x:
                project.total_delivery += sheet.total_deli

    #computing the erection amount of all drawings in the project
    def _compute_total_erection(self):
        for project in self:
            project.total_erection = 0.0
            x = self.env['construction.drawing'].search([('project_id', '=', project.id)])
            for sheet in x:
                project.total_erection += sheet.total_erec

    @api.multi
    def purchase_order_count_button(self):
        self.ensure_one()
        return {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain':  [('id', 'in', self.purchase_id.ids)],
        }


    @api.multi
    def _get_job_order_count(self):
        for order in self:
            order_ids = self.env['job.order'].search([('project_id', '=', order.id)])
            order.job_order_count = len(order_ids)
        return

    @api.multi
    def project_job_order_button(self):
        self.ensure_one()
        return {
            'name': 'Job Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.order',
            'domain': [('project_id', '=', self.id)],
        }

    @api.multi
    def _compute_issue_count(self):
        for project_id in self:
            issue_ids = self.env['project.issue'].search([('project_id','=',project_id.id)])
            count = len(issue_ids)
            project_id.issue_count = count
        return
    
    @api.multi
    def button_view_issue(self):
        issue = {}
        issue_obj = self.env['project.issue']
        issue_ids = issue_obj.search([('project_id','=',self.id)])
        total_issue = []
        for issue_id in issue_ids:
            total_issue.append(issue_id.id)
        if total_issue:
            project_project = self.env['ir.actions.act_window'].for_xml_id('bi_odoo_job_costing_management', 'project_issue_categ_act0')
            project_project['domain'] = [('id', 'in', total_issue)]
        return project_project
        
    @api.model
    def _get_alias_models(self):
        res = super(Project, self)._get_alias_models()
        res.append(("project.issue", "Issues"))
        return res

    def _issue_needaction_count(self):
        issue_data = self.env['project.issue'].read_group([('project_id', 'in', self.ids), ('message_needaction', '=', True)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in issue_data)
        for project in self:
            project.issue_needaction_count = int(result.get(project.id, 0))

    @api.multi
    def write(self, vals):
        res = super(Project, self).write(vals)
        if 'active' in vals:
            # archiving/unarchiving a project does it on its issues, too
            issues = self.with_context(active_test=False).mapped('issue_ids')
            issues.write({'active': vals['active']})
        return res
