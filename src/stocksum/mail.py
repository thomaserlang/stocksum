import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from stocksum.config import config

class Mail(object):

    @classmethod
    def send(cls, recipients, subject, message, from_base='no-reply', attachments=[]):
        '''

        :param recipients: list of str (email addresses)
        :param subject: str
        :param message: str
        :param from_base: str
        :param attachments: list of `BytesIO()`
        '''
        if not recipients:
            return
        multi_msg = MIMEMultipart()
        msg = MIMEText(
            message,
            'html'
        )
        subject = (subject[:72] + '...') if len(subject) > 72 else subject
        multi_msg['From'] = '{}@{}'.format(from_base, config['email']['from_domain'])
        multi_msg['To'] = ', '.join(recipients)
        multi_msg['Subject'] = subject
        multi_msg.attach(msg)
        for i, a in enumerate(attachments):
            a.seek(0)
            attach_msg = MIMEBase('image', 'png')
            attach_msg.add_header('Content-ID', 'image{}.png'.format(i))
            attach_msg.set_payload(a.getvalue())
            encoders.encode_base64(attach_msg)
            attach_msg.add_header(
                'Content-Disposition',
                'attachment',
                filename='image{}.png'.format(i),
            )
            multi_msg.attach(attach_msg)

        session = smtplib.SMTP(
            config['email']['server'],
            config['email']['port']
        )
        if config['email']['use_tls']:
            session.ehlo()
            session.starttls()
        session.login(
            config['email']['username'],
            config['email']['password'],
        )
        session.sendmail(
            multi_msg['From'],
            recipients,
            multi_msg.as_string()
        )
        session.quit()