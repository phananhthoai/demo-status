from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string


class Server(models.Model):
    server = models.CharField(max_length=30, unique=True)
    ip = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.server} - {self.ip}'


class State(models.Model):
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=30)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.status} - {self.updated_at} - {self.content}'


class Alert(models.Model):
    fingerprint = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=20,
                              choices=[
                                  ('UNKNOWN', 'Unknown'), ('FIRING', 'FIRING'), ('RESOLVED', 'RESOLVED')
                              ],
                              default='UNKNOWN', null=True)
    labels = models.JSONField(null=True)
    annotations = models.JSONField(null=True)
    values = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _last_status = None

    def set_status(self, next_status):
        if next_status != self.status:
            self._last_status = self.status
        self.status = next_status

    def __str__(self):
        return f'{self.fingerprint}: {self.status}'

    def build_mail_body(self):
        return render_to_string('mail.html', {
            'labels': self.labels,
            'annotations': self.annotations,
            'values': self.values,
            'status': self.status,
        })

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._last_status:
            # Thay đổi status -> gửi mail
            print('[ALERT] Send mail')
            try:
                m = EmailMultiAlternatives(
                    f'Alert {self.fingerprint}: Status {self.status}',
                    'No text',
                    "kenkukhanh@gmail.com",
                    ['thoai.phan@elofun.com'],
                )
                m.attach_alternative(self.build_mail_body(), 'text/html')
                m.send()
            except Exception as ex:
                print(f'[ALERT] Send mail failed: {ex}')
        else:
            print('[ALERT] No send mail')
