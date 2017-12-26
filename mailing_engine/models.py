from django.db import models
from django.core.mail import send_mail

# Create your models here.


class HtmlMail(object):
    subject = ''
    body = ''
    body_file = None
    # from_email = settings.DEFAULT_FROM_EMAIL
    # reply_to = settings.DEFAULT_REPLY_TO_EMAIL
    template_name = ''

    def __init__(self, request):
        super().__init__()
        self.recipient_list = set()
        self.cc_list = set()
        self.bcc_list = set()
        self.attachment_paths = []
        self.request = request

    def get_context_data(self):
        return self.context

    def get_subject(self):
        return str(self.subject)

    def get_from_email(self):
        return self.from_email

    def get_body(self, ctx):
        if self.body_file is not None:
            module_dir = os.path.dirname(__file__)  # get current directory
            file_path = os.path.join(module_dir, self.body_file)
            self.body = open(file_path).read()
        return self.body.format(**ctx)

    def render_html_body(self):
        ctx = self.get_context_data()
        return render_to_string(self.template_name, ctx)

    def send(self):
        # logger = logging.getLogger(__name__)
        # try:
            send_email.delay(
                subject=self.get_subject(),
                message=self.get_body(self.get_context_data()),
                from_email=self.get_from_email(),
                reply_to=[self.reply_to],
                recipient_list=list(self.recipient_list),
                cc_list=list(self.cc_list),
                bcc_list=list(self.bcc_list),
                html_message=self.render_html_body(),
                attachments_paths=self.attachment_paths
            )
        # # In case celery could not connect to redis or reach '_kombu.binding.celery' key from database
        # except (InconsistencyError, redis.exceptions.ConnectionError) as e:
        #     logger.error('Cannot send email asynchronously', extra={'stack': True})
        #     send_email(
        #         subject=self.get_subject(),
        #         message=self.get_body(self.get_context_data()),
        #         from_email=self.get_from_email(),
        #         reply_to=[self.reply_to],
        #         recipient_list=list(self.recipient_list),
        #         cc_list=list(self.cc_list),
        #         bcc_list=list(self.bcc_list),
        #         html_message=self.render_html_body(),
        #         attachments_paths=self.attachment_paths
        #     )

    def add_recipients(self, *args):
        self.recipient_list.update(list(args))
        return self

    def add_bccs(self, *args):
        self.bcc_list.update(list(args))
        return self

    def add_ccs(self, *args):
        self.cc_list.update(list(args))
        return self

    def add_attachment(self, file):
        media_mails_path = os.path.join(settings.MEDIA_ROOT, 'mails')
        if not os.path.exists(media_mails_path):
            os.makedirs(media_mails_path)
        filename = 'mails/%s' % file.name
        file_path = default_storage.save(filename, ContentFile(file.read()))
        file_info = {
            "file_path": file_path,
            "content_type": file.content_type
        }
        self.attachment_paths.append(file_info)