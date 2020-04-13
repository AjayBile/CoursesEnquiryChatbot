import os, smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from smtplib import SMTPNotSupportedError


class SendMails():

    def __init__(self, mailServer: str, mailPort: int, emailUser: str, emailPass: str):
        try:

            self.server = smtplib.SMTP(mailServer, mailPort)
            self.server.starttls()
            self.server.login(emailUser, emailPass)

        except SMTPNotSupportedError:
            print("Authentication not supported for Mail Server "+mailServer)
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)

    def SendMail(self, senderAddress: str, toAddress: str, subject: str, mailBody: str, attachmentPath: str = None, attachmentFileName: str = None,
                 intendedPerson: str = None, customerInfo: dict = None):

        body: str = ""
        try:
            msg = MIMEMultipart()
            # msg.set_content(body)

            msg['From'] = senderAddress
            msg['To'] = toAddress
            msg['Subject'] = subject


            if intendedPerson == "SalesTeam":

                """Creating Sales Team Mail Body Part"""

                # open the file to be sent
                msgbody = open("email_templates//"+mailBody+".html", "r")

                # instance of MIMEBase and named as p
                p = MIMEBase('application', 'octet-stream')

                body = msgbody.read()

                body = body.replace('cust_name', customerInfo.get('cust_name'))
                body = body.replace('cust_contact', customerInfo.get('cust_contact'))
                body = body.replace('cust_email', customerInfo.get('cust_email'))
                body = body.replace('course_name', customerInfo.get('course_name'))

                msg.attach(MIMEText(body, 'html'))

            else:

                """Mail sending attachment part for Sales Team"""

                body = mailBody

                msg.attach(MIMEText(body, 'plain'))

                if attachmentPath:
                    if os.path.exists(attachmentPath):

                        # open the file to be sent
                        attachment = open(attachmentPath, "rb")

                        # instance of MIMEBase and named as p
                        p = MIMEBase('application', 'octet-stream')

                        # To change the payload into encoded form
                        p.set_payload((attachment).read())

                        # encode into base64
                        encoders.encode_base64(p)

                        if not attachmentFileName:
                            attachmentFileName = os.path.basename(attachmentPath)

                        p.add_header('Content-Disposition', "attachment; filename= %s" % attachmentFileName)

                        # attach the instance 'p' to instance 'msg'
                        msg.attach(p)

            text = msg.as_string()
            self.server.sendmail(senderAddress, toAddress, text)

        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print("An exception has occured in MailSending file")
            print(message)