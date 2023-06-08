from odoo import fields, models, api
from ast import literal_eval
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re


class DocumentAlerts(models.Model):
    _name = 'document.alerts'
    _description = 'Document Alerts'

    name = fields.Char(default="New")
    reminder_ids = fields.Many2many(comodel_name='days.reminder.line', string='Reminders', store=True)
    partner_ids = fields.Many2many(comodel_name='res.partner', string='Partner')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Employee')
    document_type_id = fields.Many2one(comodel_name='document.type', string='Document Type')
    attach_type = fields.Selection(string='Attach Type', selection=[('PDF', 'PDF'), ('IMAGE', 'IMAGE'), ])
    attachment_name = fields.Char()
    email_cc = fields.Char(string="Email CC")
    image_attach = fields.Binary(string="Image")
    pdf_attach = fields.Binary(string="PDF")
    expiry_date = fields.Date(string="Expiry Date")
    desc = fields.Text(string="Desc")

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

    def document_exp_reminder(self):
        # days_reminder_ids = self.env['ir.config_parameter'].get_param(
        #     'wt_alerts.days_reminder_ids') or []
        # days_reminder_ids = literal_eval(days_reminder_ids)
        # reminder_ids = self.env['days.reminder.line'].search([('id', 'in', days_reminder_ids)])
        # print("reminder_ids", reminder_ids)
        # print(self.reminder_ids)
        for line in self.env['document.alerts'].search([]):
            for rec in line.reminder_ids:
                ndays = rec.ndays
                current_date = fields.date.today() + relativedelta(days=ndays)
                if line.expiry_date == current_date:
                    users = self.env.ref('wt_alerts.document_expiry_reminder_group').users
                    summary = '{} Document Expiry reminder Document #: {} will be expired after: {} days '.format(
                        rec.name,
                        line.name,
                        ndays)
                    subject = '{} Document Expiry reminder'.format(rec.name)
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    body = 'Document #:{} will be expired after: {} days '.format(line.name,
                                                                                  ndays) + ' click here to open: <a target=_BLANK href="{}/web?#id='.format(
                        base_url) + str(
                        line.id) + '&view_type=form&model=document.alerts&action=" style="font-weight: bold">' + str(
                        line.name) + '</a>'
                    arabic_body = '<p>يرجي العلم بأن الوثيقة #:{} ستنتهي بعد: {} يوم'.format(line.name,
                                                                                          ndays) + ' من فضلك اضغط علي الرابط لفتح الوثيقة: <a target=_BLANK href="{}/web?#id='.format(
                        base_url) + str(
                        line.id) + '&view_type=form&model=document.alerts&action=" style="font-weight: bold">' + str(
                        line.name) + '</a>\n</p>' + '<p>\nDocument #:{} will be expired after: {} days '.format(line.name,
                                                                                                         ndays) + ' click here to open: <a target=_BLANK href="{}/web?#id='.format(
                        base_url) + str(
                        line.id) + '&view_type=form&model=document.alerts&action=" style="font-weight: bold">' + str(
                        line.name) + '</a></p>'
                    for user in users:
                        if user.partner_id.email:
                            values = {
                                'subject': subject,
                                'author_id': self.env.company.partner_id.id,
                                'email_to': user.partner_id.email,
                                'email_from': 'no-reply@wtsaudi.com',
                                'state': 'outgoing',
                                'body_html': arabic_body,
                                # 'recipient_ids': self.partner_id,
                                # 'attachment_ids': [(6, 0, [x for x in attachments])],
                            }
                            template = self.env['mail.mail'].create(values)
                            template.send()
                    if line.partner_ids:
                        for partner in self.partner_ids:
                            if partner.email:
                                values = {
                                    'subject': subject,
                                    'author_id': self.env.company.partner_id.id,
                                    'email_to': partner.email,
                                    'email_from': 'no-reply@wtsaudi.com',
                                    'state': 'outgoing',
                                    'body_html': arabic_body,
                                    # 'recipient_ids': self.partner_id,
                                    # 'attachment_ids': [(6, 0, [x for x in attachments])],
                                }
                                template = self.env['mail.mail'].create(values)
                                template.send()
                    if line.user_id.partner_id.email:
                        values = {
                            'subject': subject,
                            'author_id': self.env.company.partner_id.id,
                            'email_to': self.user_id.partner_id.email,
                            'email_from': 'no-reply@wtsaudi.com',
                            'state': 'outgoing',
                            'body_html': arabic_body,
                            # 'recipient_ids': self.partner_id,
                            # 'attachment_ids': [(6, 0, [x for x in attachments])],
                        }
                        template = self.env['mail.mail'].create(values)
                        template.send()
                    if line.employee_ids:
                        for emp in self.employee_ids:
                            if emp.work_email:
                                values = {
                                    'subject': subject,
                                    'author_id': self.env.company.partner_id.id,
                                    'email_to': emp.work_email,
                                    'email_from': 'no-reply@wtsaudi.com',
                                    'state': 'outgoing',
                                    'body_html': arabic_body,
                                    # 'recipient_ids': self.partner_id,
                                    # 'attachment_ids': [(6, 0, [x for x in attachments])],
                                }
                                template = self.env['mail.mail'].create(values)
                                template.send()
                    # print(body, "=====", subject)
                    email_list = (line.email_cc.split(","))
                    if email_list:
                        for email in email_list:
                            values = {
                                'subject': subject,
                                'author_id': self.env.company.partner_id.id,
                                'email_to': email,
                                'email_from': 'no-reply@wtsaudi.com',
                                'state': 'outgoing',
                                'body_html': arabic_body,
                                # 'recipient_ids': self.partner_id,
                                # 'attachment_ids': [(6, 0, [x for x in attachments])],
                            }
                            template = self.env['mail.mail'].create(values)
                            template.send()


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
