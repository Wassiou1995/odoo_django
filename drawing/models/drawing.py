from odoo import fields, models, api, _, SUPERUSER_ID
from datetime import datetime


class ConstructionDrawing (models.Model):
    _name = 'construction.drawing'
    _description = 'Items Records for Projects'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    pricing_id = fields.Many2one('construction.pricing', string='Pricing', required=True)
    item_ids = fields.One2many('item.number', 'drawing_id', string='Item Code', copy=True)
    Division = fields.Selection([('GRC', 'GRC'),('GRP', 'GRP'),('GRG','GRG'),('MOULD', 'MOULD'),('STEEL', 'STEEL')],)
    Building = fields.Char(String='Building')
    name_seq = fields.Char(string='Drawing No', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    create_date = fields.Datetime(string="Create Date", default=datetime.now())
    close_date = fields.Datetime(string="Close Date", default=datetime.now())
    create_by_id = fields.Many2one('res.users', 'Created By')
    confirmed_by_id = fields.Many2one('res.users', string="Confirmed By", copy=False)
    department_manager_id = fields.Many2one('res.users', string="Department Manager", copy=False)
    approved_by_id = fields.Many2one('res.users', string="Approved By", copy=False)
    rejected_by = fields.Many2one('res.users', string="Rejected By", copy=False)
    confirmed_date = fields.Date(string="Confirmed Date", readonly=True, copy=False)
    department_approval_date = fields.Date(string="Department Approval Date", readonly=True, copy=False)
    approved_date = fields.Date(string="Approved Date", readonly=True, copy=False)
    rejected_date = fields.Date(string="Rejected Date", readonly=True, copy=False)
    reason_for_requisition = fields.Text(string="Reason For Requisition")
    state = fields.Selection([
        ('new', 'New'),
        ('department_approval', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting User Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel')], string='Stage', copy=False, default="new")
    active = fields.Boolean(default=True, help="If the active field is set to False")
    """la somme de tout les drawings """
    total_drawing = fields.Float(String='Total Drawing', compute='_compute_total_drawing')
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    #Calculate the total amount of any department in one drawing
    total_prod = fields.Float(String='Amount Production', compute='_compute_total_prod')
    total_deli = fields.Float(String='Amount Delivery', compute='_compute_total_deli')
    total_erec = fields.Float(String='Amount Erection', compute='_compute_total_erec')
    type_name = fields.Char('Type Name', compute='_compute_type_name')
    total_volume = fields.Char('Total Volume', compute='_compute_total_volume')



    '''
    @api.onchange('pricing_id')
    def onchange_partner_id(self):
        for rec in self:
            return {'domain': {'pricing_id': [('project_id', '=', rec.pricing_id.project_id)]}}
    '''

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('drawing.boq_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in ('draft', 'sent', 'cancel') else _('Sales Order')

    #mail template
    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('drawing', 'boq_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'construction.drawing', self.ids[0])
        ctx = {
            'default_model': 'construction.drawing',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def force_quotation_send(self):
        for order in self:
            email_act = order.action_quotation_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.company_id.email)
                order.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    # the currency of project
    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id.id

    '''
        This function give status for the drawing 
    '''
    @api.multi
    def print_quotation(self):
        return self.env.ref('drawing.report_boq').report_action(self)

    @api.multi
    def confirm_drawing(self):
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

    '''
            This function create a sequence for the drawing loaded by default
    '''

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('construction.drawing') or _('New')
        result = super(ConstructionDrawing, self).create(vals)
        return result

    @api.multi
    def pricing(self):
        self.ensure_one()
        return {
            'name': _('Pricing'),
            'domain': [('drawing_id', '=', self.id)],
            'res_model': 'construction.pricing',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d,'default_drawing_id': %d}" % (self.project_id.id, self.id)
        }

    #Compute the total amount of the drawing in the project
    @api.multi
    @api.depends('item_ids.Amount_total')
    def _compute_total_drawing(self):
        for line in self:
            total_drawing = 0.0
            for rec in line.item_ids:
                total_drawing += rec.Amount_total
            line.update({
                'total_drawing': total_drawing,
            })

    #Compute the Volume of item
    @api.multi
    def _compute_total_volume(self):
        total = 0.0
        for rec in self.item_ids:
            total += rec.Volume
        self.total_volume = total


    # compute the amount of any department
    @api.multi
    @api.depends('item_ids.Amount_prod')
    def _compute_total_prod(self):
        for line in self:
            total_prod = 0.0
            for rec in line.item_ids:
                total_prod += rec.Amount_prod
            line.update({
                'total_prod': total_prod,
            })

    @api.multi
    @api.depends('item_ids.Amount_deli')
    def _compute_total_deli(self):
        for line in self:
            total_deli = 0.0
            for rec in line.item_ids:
                total_deli += rec.Amount_deli
            line.update({
                'total_deli': total_deli,
            })

    @api.multi
    @api.depends('item_ids.Amount_erec')
    def _compute_total_erec(self):
        for line in self:
            total_erec = 0.0
            for rec in line.item_ids:
                total_erec += rec.Amount_erec
            line.update({
                'total_erec': total_erec,
            })

    '''
    @api.onchange('pricing_id')
    @api.depends('pricing_id')
    def onchange_product_id(self):
        for rec in self:
            # lines = ([5, 0, 0])
            lines = []
            for line in self.item_ids:
                vals = {
                    'pricing_id': self.pricing_id,
                    'UR_production': self.pricing_id.UR_production,
                    'UR_delivery': self.pricing_id.UR_delivery,
                    'UR_erection': self.pricing_id.UR_erection,
                }
                lines.append(vals)
            rec.item_ids = lines
    '''


#the items & sub items
class ItemNumber (models.Model):
    _name = 'item.number'
    _description = 'Items Records for Projects Lines'
    _rec_name = 'title'

    @api.model
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    title = fields.Char('Item No', required=True)
    drawing_id = fields.Many2one('construction.drawing', 'Drawing')
    Type = fields.Char('Type')
    Type_of_finish = fields.Char('Type of finish')
    Length = fields.Float('Length', required=True)
    Width = fields.Float('Width', required=True)
    Height = fields.Float('Height', required=True)
    Thick = fields.Float('Thick', required=True)
    Quantity = fields.Integer('Quantity', required=True)
    Volume = fields.Float('Volume', compute='_compute_total', required=True)
    Unit = fields.Many2one('uom.uom', 'Unit Of Measure')

    # get the unit pricing for each department
    UR_production = fields.Float(String='UR Production')
    UR_delivery = fields.Float(String='UR Delivery')
    UR_erection = fields.Float(String='UR Erection')

    #get the amount of departments
    Amount_prod = fields.Float(String='Amount Production', compute='_compute_total_production', required=True)
    Amount_deli = fields.Float(String='Amount Delivery', compute='_compute_total_delivery', required=True)
    Amount_erec = fields.Float(String='Amount Erection', compute='_compute_total_erection', required=True)

    # get the Total unit sum of three units
    UR_total = fields.Float(String='Unit Rate Total', compute='_compute_total_UR', required=True)
    Amount_total = fields.Float(String='Amount Total', compute='_compute_total_amount', required=True)
    pricing_id = fields.Many2one('construction.pricing', String='Pricing',
                                 default=lambda self: self.env.context.get('drawing_id'))
    # the unit rate of project with currency
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    Unit_Production = fields.Float(String='Unit Production', compute='_compute_unit_production', required=True)
    Unit_Delivery = fields.Float(String='Unit Delivery', compute='_compute_unit_delivery', required=True)
    Unit_Erection = fields.Float(String='Unit Erection', compute='_compute_unit_erection', required=True)
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the estimation without removing it.")
    stage_id = fields.Many2one('project.item.type', string='Stage', ondelete='restrict', track_visibility='onchange',
                               index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               domain="[('project_ids', '=', project_id)]", copy=False)
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label',
                                     track_visibility='onchange')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)



    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    '''
    # get the unit rate price from pricing or this project
    @api.multi
    @api.onchange('pricing_id')
    def onchange_pricing_id(self):
        res = {}
        if not self.pricing_id:
            return res
        self.UR_production = self.pricing_id.UR_production
        self.UR_delivery = self.pricing_id.UR_delivery
        self.UR_erection = self.pricing_id.UR_erection
    '''

    # get the unit rate price from pricing or this project
    @api.multi
    @api.onchange('pricing_id')
    def onchange_pricing_id(self):
        res = {}
        if not self.pricing_id:
            return res
        self.UR_production = self.pricing_id.UR_production
        self.UR_delivery = self.pricing_id.UR_delivery
        self.UR_erection = self.pricing_id.UR_erection

    #open the item codes
    @api.multi
    def open_bom(self):
        self.ensure_one()
        return {
            'name': _('Details'),
            'domain': [('item_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'item.code',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'default_item_id': %d}" % (self.id)

        }

    #Compute Volume of an item
    @api.multi
    @api.depends('Length', 'Width', 'Height')
    def _compute_total(self):
        for rec in self:
            rec.Volume = rec.Length * rec.Width * rec.Height

    #Compute the total units in the pricing
    @api.multi
    @api.depends('UR_production', 'UR_delivery', 'UR_erection')
    def _compute_total_UR(self):
        for rec in self:
            rec.UR_total = rec.UR_production + rec.UR_delivery + rec.UR_erection

    #Compute the total amounts of departments
    @api.multi
    @api.depends('Amount_prod', 'Amount_deli', 'Amount_erec')
    def _compute_total_amount(self):
        for rec in self:
            rec.Amount_total = rec.Amount_prod + rec.Amount_deli + rec.Amount_erec

    @api.multi
    @api.depends('Amount_prod' , 'Quantity', 'Unit_Production')
    def _compute_total_production(self):
        for rec in self:
            rec.Amount_prod = rec.Quantity * rec.Unit_Production

    @api.multi
    @api.depends('Amount_deli', 'Unit_Delivery', 'Quantity')
    def _compute_total_delivery(self):
        for rec in self:
            rec.Amount_deli = rec.Quantity * rec.Unit_Delivery

    @api.multi
    @api.depends('Amount_erec', 'Unit_Erection', 'Quantity')
    def _compute_total_erection(self):
        for rec in self:
            rec.Amount_erec = rec.Quantity * rec.Unit_Erection

    # Compute Unit rates of amount
    @api.multi
    @api.depends('Unit_Production','UR_production', 'Volume')
    def _compute_unit_production(self):
        for rec in self:
            rec.Unit_Production = rec.UR_production * rec.Volume

    @api.multi
    @api.depends('Unit_Delivery','UR_delivery', 'Volume')
    def _compute_unit_delivery(self):
        for rec in self:
            rec.Unit_Delivery = rec.UR_delivery * rec.Volume

    @api.multi
    @api.depends('Unit_Erection', 'UR_erection', 'Volume')
    def _compute_unit_erection(self):
        for rec in self:
            rec.Unit_Erection = rec.UR_erection * rec.Volume

    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id.id




    @api.multi
    @api.onchange('pricing_id')
    def onchange_pricing_id(self):
        res = {}
        if not self.pricing_id:
            return res
        self.pricing_id = self.drawing_id.pricing_id

    # ITEM CODE
    class ItemCode(models.Model):
        _name = 'item.code'
        _description = 'Item Code'
        _inherit = ['mail.thread', 'mail.activity.mixin']
        _rec_name = 'title'
        _order = 'sequence,id'

        item_id = fields.Many2one('item.number', string='Item No',
                                  required=True, default=lambda self: self.env.context.get('item_id'))
        title = fields.Char('Item Code', required=True)
        Image = fields.Binary(String='image')
        sequence = fields.Integer('Item Code number', default=10)
        description = fields.Html('Description', translate=True, oldname="note",
                                  help="An introductory text to your page")
        sub_ids = fields.One2many('item.sub', 'code_id', string='Item Subs', copy=True)
        Type = fields.Char('Type')
        Type_of_finish = fields.Char('Type of finish')
        Length = fields.Char('Length', required=True)
        Width = fields.Char('Width', required=True)
        Height = fields.Char('Height', required=True)
        Thick = fields.Char('Thick', required=True)
        Quantity = fields.Char('Quantity', required=True)
        Unit = fields.Many2one('uom.uom','Unit Of Measure')

    class ItemSub(models.Model):
        _name = 'item.sub'
        _description = 'Item Sub'
        _rec_name = 'title'
        _order = 'sequence,id'

        # Model fields #
        title = fields.Char('Item Sub', required=True, translate=True)
        code_id = fields.Many2one('item.code', string='Item Code', required=True,
                                  default=lambda self: self.env.context.get('code_id'))
        sequence = fields.Integer('Sequence', default=10)
        Image = fields.Binary(String='image')
        Length = fields.Char('Length', required=True)
        Width = fields.Char('Width', required=True)
        Height = fields.Char('Height', required=True)
        Thick = fields.Char('Thick', required=True)
        Quantity = fields.Char('Quantity', required=True)
        Unit = fields.Many2one('uom.uom', 'Unit Of Measure')

    # RES PARTNER inherit
    class Partner(models.Model):
        _inherit = 'res.partner'

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('mail_template_demo.example_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)


class ProjectItemType(models.Model):
    _name = 'project.item.type'
    _description = 'item Stage'
    _order = 'sequence, id'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id',
                                       string='Projects',
                                       default=_get_default_project_ids)
    legend_priority = fields.Char(
            string='Starred Explanation', translate=True,
            help='Explanation text to help users using the star on tasks or issues in this stage.')
    legend_blocked = fields.Char(
            'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
            help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
            'Green Kanban Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True,
            help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
            'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
            help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
            'mail.template',
            string='Email Template',
            domain=[('model', '=', 'project.task')],
            help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                              help='This stage is folded in the kanban view when there are no records in that stage to display.')
    rating_template_id = fields.Many2one(
            'mail.template',
            string='Rating Email Template',
            domain=[('model', '=', 'project.task')],
            help="If set and if the project's rating configuration is 'Rating when changing stage', then an email will be sent to the customer when the task reaches this step.")
    auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False,
                                                      help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
                                                           " * A good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
                                                           " * A medium or a bad feedback will set the kanban state to 'blocked' (red bullet).\n")



    @api.multi
    def unlink(self):
        stages = self
        default_project_id = self.env.context.get('default_project_id')
        if default_project_id:
            shared_stages = self.filtered(
                lambda x: len(x.project_ids) > 1 and default_project_id in x.project_ids.ids)
            tasks = self.env['project.task'].with_context(active_test=False).search(
                [('project_id', '=', default_project_id), ('stage_id', 'in', self.ids)])
            if shared_stages and not tasks:
                shared_stages.write({'project_ids': [(3, default_project_id)]})
                stages = self.filtered(lambda x: x not in shared_stages)
            return super(ProjectItemType, stages).unlink()