import logging

from odoo import fields, models, api, _

import base64
import requests
from odoo.exceptions import UserError, ValidationError
import json
from email.message import EmailMessage
import re
import email as eee
from urllib3.filepost import encode_multipart_formdata

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    # def send(self, auto_commit=False, raise_exception=False):
    #     request_url = "https://email.wide-techno.com/api/send-mail"
    #     for rec in self:
    #         to = []
    #         html_body = rec.body_html
    #         html_body = html_body.replace('"', "'")
    #         email_to = rec.email_to
    #         email_cc = rec.email_cc
    #         reply_to = rec.reply_to
    #         email_to_false = False
    #         if email_to:
    #             for i in email_to:
    #                 if i == "<" or i == ">":
    #                     email_to_false = True
    #                     break
    #         email_cc_false = False
    #         if email_cc:
    #             for i in email_cc:
    #                 if i == "<" or i == ">":
    #                     email_cc_false = True
    #                     break
    #         reply_to_false = False
    #         if reply_to:
    #             for i in reply_to:
    #                 if i == "<" or i == ">":
    #                     reply_to_false = True
    #                     break
    #         if email_to:
    #             if email_to_false:
    #                 start = email_to.find("<") + len("<")
    #                 # end = len(email_to)
    #                 end = email_to.find(">")
    #                 email_to = email_to[start:end]
    #             to.append(email_to)
    #         if rec.recipient_ids:
    #             for email in rec.recipient_ids:
    #                 to.append(email.email)
    #         if email_cc:
    #             if email_cc_false:
    #                 start = email_cc.find("<") + len("<")
    #                 end = email_cc.find(">")
    #                 email_cc = email_cc[start:end]
    #         if reply_to:
    #             if reply_to_false:
    #                 start = reply_to.find("<") + len("<")
    #                 end = reply_to.find(">")
    #                 reply_to = reply_to[start:end]
    #         # print(to)
    #         attached = []
    #         # for line in rec.attachment_ids:
    #         #     attached.append(base64.decodebytes(line.datas))
    #         #     print(line.datas)
    #         #     print(attached)
    #         #     print(json.load(line.datas))
    #         IrAttachment = self.env['ir.attachment']
    #         body = rec.body_html or ''
    #         attachments = rec.attachment_ids
    #         for link in re.findall(r'/web/(?:content|image)/([0-9]+)', body):
    #             attachments = attachments - IrAttachment.browse(int(link))
    #
    #         # load attachment binary data with a separate read(), as prefetching all
    #         # `datas` (binary field) could bloat the browse cache, triggerring
    #         # soft/hard mem limits with temporary data.
    #         attachments = [(a['name'], base64.b64decode(a['datas']), a['mimetype'])
    #                        for a in attachments.sudo().read(['name', 'datas', 'mimetype']) if a['datas'] is not False]
    #         print()
    #         msg = EmailMessage(policy=eee.policy.SMTP)
    #         for (fname, fcontent, mime) in attachments:
    #             maintype, subtype = mime.split('/') if mime and '/' in mime else ('application', 'octet-stream')
    #             msg.add_attachment(fcontent, maintype, subtype, filename=fname)
    #         print(msg)
    #         body = {
    #             "to": to,
    #             "subject": rec.subject,
    #             "reply_to_email": reply_to,
    #             "sender_name": rec.author_id.name,
    #             "attachments": [msg],
    #             "body": html_body + "\n <p style='text-align:center'>نظام التواصل من التقنية الموسعة</p>"
    #         }
    #         if email_cc:
    #             body["cc"] = [email_cc]
    #         body = json.dumps(body, indent=4)
    #         msg[""]
    #         print("body:", body)
    #
    #         headers = {
    #             "Accept": "application/json",
    #             "Content-Type": "application/json",
    #             "Client-Id": "rP93dJ3qKmQEHvFyyPqtcfo3c2fSTTZC1bxOjnnphya0hLSKwL",
    #             "Client-Secret": "Ta4seQUdqneFffJRPZJjO1nH5CJkNA6RFg7X9U9Q6KNWguc6fp4E91c6jETTL3bDbpbhzrqB8pQ60xbYvXSGaOz01p",
    #         }
    #         try:
    #             request_response = requests.request('POST', request_url, data=body, headers=headers, timeout=(5, 10))
    #             # print("request_response:", request_response)
    #             # if request_response:
    #             #     _logger.warning('%s.' % request_response.text)
    #         except Exception as ex:
    #             raise ValidationError(_('%s' % ex))
    #         if request_response.ok:
    #             rec.state = 'received'
    #             response_data = request_response.json()
    #             # token = response_data.get('access_token')
    #             # print("Error In Response:", response_data)
    #         else:
    #
    #             response_data = request_response.json()
    #             # token = response_data.get('access_token')
    #             # print("response_data:", response_data['message'])
    #     return

    def send(self, auto_commit=False, raise_exception=False):
        request_url = "https://email.wide-techno.com/api/send-mail"
        for rec in self:
            to = []
            html_body = rec.body_html
            html_body = html_body.replace('"', "'")
            email_to = rec.email_to
            email_cc = rec.email_cc
            reply_to = rec.reply_to
            email_to_false = False

            if email_to:
                for i in email_to:
                    if i == "<" or i == ">":
                        email_to_false = True
                        break
            email_cc_false = False
            if email_cc:
                for i in email_cc:
                    if i == "<" or i == ">":
                        email_cc_false = True
                        break
            reply_to_false = False
            if reply_to:
                for i in reply_to:
                    if i == "<" or i == ">":
                        reply_to_false = True
                        break
            if email_to:
                if email_to_false:
                    start = email_to.find("<") + len("<")
                    # end = len(email_to)
                    end = email_to.find(">")
                    email_to = email_to[start:end]
                to.append(email_to)
            if rec.recipient_ids:
                for email in rec.recipient_ids:
                    to.append(email.email)
            if email_cc:
                if email_cc_false:
                    start = email_cc.find("<") + len("<")
                    end = email_cc.find(">")
                    email_cc = email_cc[start:end]
            if reply_to:
                if reply_to_false:
                    start = reply_to.find("<") + len("<")
                    end = reply_to.find(">")
                    reply_to = reply_to[start:end]
            # print(to)
            att_links = []
            if rec.attachment_ids:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web/content/'
                for line in rec.attachment_ids:
                    line.access_token = True
                    link = url + str(line.id) + '?download=true&access_token=' + str(
                        line.access_token)
                    att_links.append(link)
            final_body = html_body + "\n <p style='text-align:center'>نظام التواصل من التقنية الموسعة</p>\n"
            if att_links:
                final_body += "\n <p style='text-align:center'>الرجاء مراجعه المرفقات من خلال اللينكات التاليه</p>\n"
            for link in att_links:
                final_body += "\n" + "<a href='%s'>%s</a>" % (link, link)
            body = {
                "to": to,
                "subject": rec.subject,
                "reply_to_email": reply_to,
                "sender_name": rec.author_id.name,
                "body": final_body}
            if email_cc:
                body["cc"] = [email_cc]
            body = json.dumps(body, indent=4)
            print("body:", body)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Client-Id": "rP93dJ3qKmQEHvFyyPqtcfo3c2fSTTZC1bxOjnnphya0hLSKwL",
                "Client-Secret": "Ta4seQUdqneFffJRPZJjO1nH5CJkNA6RFg7X9U9Q6KNWguc6fp4E91c6jETTL3bDbpbhzrqB8pQ60xbYvXSGaOz01p",
            }
            try:
                request_response = requests.request('POST', request_url, data=body, headers=headers, timeout=(5, 10))
                # print("request_response:", request_response)
                # if request_response:
                #     _logger.warning('%s.' % request_response.text)
            except Exception as ex:
                raise ValidationError(_('%s' % ex))
            if request_response.ok:
                rec.state = 'received'
                response_data = request_response.json()
                # token = response_data.get('access_token')
                # print("Error In Response:", response_data)
            else:

                response_data = request_response.json()
                _logger.error(response_data)
                # token = response_data.get('access_token')
                # print("response_data:", response_data['message'])
        return
