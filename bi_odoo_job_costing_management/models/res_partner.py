# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    issue_count = fields.Integer(compute='_compute_issue_count', string='# Issues')

    def _compute_issue_count(self):
        Issue = self.env['project.issue']
        for partner in self:
            partner.issue_count = Issue.search_count([('partner_id', 'child_of', partner.commercial_partner_id.id)])

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('bi_odoo_job_costing_management.boq_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)
