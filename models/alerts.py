import logging
import re

from odoo import fields, models, api
from ast import literal_eval
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class DocumentAlerts(models.Model):
    _name = 'document.alerts'
    _description = 'Document Alerts'

    name = fields.Char(default="New")
    reminder_ids = fields.Many2many(comodel_name='days.reminder.line', string='Reminders', store=True)
    partner_ids = fields.Many2many(
        comodel_name='res.partner', 
        string='Partner',
        domain=lambda self:[("email", "!=", False),]
        )
    user_id = fields.Many2one(
            comodel_name='res.users',
            string='User',
            domain=lambda self:[("groups_id", "=", self.env.ref("base.group_user").id),]
        )
    
    employee_ids = fields.Many2many(
        comodel_name='hr.employee', 
        string='Employee',
        domain=lambda self:[("work_email", "!=", False),]
        )
    document_type_id = fields.Many2one(comodel_name='document.type', string='Document Type')
    attach_type = fields.Selection(string='Attach Type', selection=[('PDF', 'PDF'), ('IMAGE', 'IMAGE'), ])
    attachment_name = fields.Char()
    email_cc = fields.Char(string="Email CC")
    image_attach = fields.Binary(string="Image")
    pdf_attach = fields.Binary(string="PDF")
    expiry_date = fields.Date(string="Expiry Date")
    desc = fields.Text(string="Desc")
    alert_url = fields.Char(compute='_compute_url')
    email_to = fields.Text(compute='_compute_email_to')
    remaining_days = fields.Integer(compute='_compute_remaining_days')
    is_sendable = fields.Boolean(compute='_compute_is_sendable')
    is_expired = fields.Boolean(compute='_compute_is_expired')


    @api.onchange('email_cc')
    def check_email_cc(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if self.email_cc:
            email_list = (self.email_cc.split(","))
            for i in email_list:
                if re.fullmatch(regex, i):
                    pass
                else:
                    raise ValidationError("Invalid Email")


    @api.onchange('attach_type')
    def onchange_attach_type(self):
        for rec in self:
            rec.image_attach = False
            rec.pdf_attach = False

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('wide.documents.alert.seq') or 'New'
        result = super(DocumentAlerts, self).create(values)
        return result
    

    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for rec in self:
            rec.alert_url = f"{base_url}/web?#id={rec.id}&view_type=form&model=document.alerts&action="


    @api.depends('user_id', 'employee_ids')
    def _compute_email_to(self):
        permitted_emails = [user.partner_id.email for user in self.env.ref('wt_alerts.document_expiry_reminder_group').users if user.partner_id.email]
        for rec in self:
            # _logger.debug(' Compute Is Email_to ')
            # _logger.info(f'Premitted Emails {permitted_emails} ')
            emails = []
            emails += permitted_emails
            emails += [partner.email for partner in rec.partner_ids if partner.email]
            # _logger.info(f'+ Partner Emails {emails} ')
            emails += [emp.work_email for emp in rec.employee_ids if emp.work_email]
            # _logger.info(f'+ Employee Emails {emails} ')
            emails += [rec.user_id.partner_id.email] if rec.user_id.partner_id.email else []
            # _logger.info(f'+ User Email {emails} ')
            rec.email_to = ','.join(set(emails)) or 'no-reply@wtsaudi.com'
            # _logger.info(f'Email To {rec.email_to} ')


    @api.depends('expiry_date')
    def _compute_remaining_days(self):
        for rec in self:
            delta = rec.expiry_date - fields.date.today()
            rec.remaining_days = delta.days


    @api.depends('user_id', 'employee_ids', 'email_cc', 'document_type_id', 'is_expired')
    def _compute_is_sendable(self):
        for rec in self:
            # _logger.info(' Compute Is Sendable ')
            # _logger.info(f'Not expired = {not rec.is_expired}')
            # _logger.info( f'ُEmail cc = {rec.email_cc}')
            # _logger.info(f'All condition = {(not rec.is_expired) and (rec.email_to or rec.email_cc) and rec.document_type_id}')
            rec.is_sendable = (not rec.is_expired) and (rec.email_to or rec.email_cc) and rec.document_type_id

    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        for rec in self:
            # _logger.info(' Compute Is Expired ')
            # _logger.info(f'Expiry date: {rec.expiry_date}')
            if rec.expiry_date:
                rec.is_expired = rec.expiry_date < fields.date.today()
            else:
                rec.is_expired = True
            # _logger.info(f'Is Expired: {rec.is_expired}')
    

    def action_send_email(self):
        if self.is_sendable:
            values = {
                        'author_id': self.env.company.partner_id.id,
                        'state': 'outgoing',
                    }
            template_id = self.env.ref('wt_alerts.email_template_wt_document_alerts').id
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True, email_values=values)


    def document_exp_reminder(self):
        for alert in self.env['document.alerts'].search([]):
            if [x for x in alert.reminder_ids if x.due_date == alert.expiry_date]:
                alert.action_send_email()




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ndays = fields.Integer(related='company_id.ndays', readonly=False)
    days_reminder_ids = fields.Many2many(comodel_name='days.reminder.line', string='Days Reminder', )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        days_reminder_ids = get_param('wt_alerts.days_reminder_ids', '[]')
        days_reminder_ids = [(6, 0, literal_eval(days_reminder_ids))]
        res.update(days_reminder_ids=days_reminder_ids)
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('wt_alerts.days_reminder_ids', self.days_reminder_ids.ids)
        return res


class DaysReminderLine(models.Model):
    _name = 'days.reminder.line'
    _description = ''

    name = fields.Char(string="Description", required=True)
    type = fields.Selection(string='Type', selection=[('After', 'After'), ('Before', 'Before'), ])
    ndays = fields.Integer(string="# of Days Before Expiry Date", required=True)
    
    @property
    def due_date(self):
        return fields.date.today() + relativedelta(days=self.ndays)
