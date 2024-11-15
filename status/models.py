from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from requests import request
from demo.settings import API_VOICE

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



    def get_audio(self):
        url = 'https://api.fpt.ai/hmi/tts/v5'
        payload = f'Lỗi { self.labels["alertname"] } tại server { self.labels["nodename"] }'
        headers = {
            'api-key': API_VOICE,
            'speed': '',
            'voice': 'linhsan'
        }
        response = request('POST', url, data=payload.encode('utf-8'), headers=headers)

        return response.json().get('async')


    def build_mail_body(self):
        if self.annotations['level'] == 'Critical':
            return render_to_string('mail.html', {
                'labels': self.labels,
                'annotations': self.annotations,
                'values': self.values,
                'status': self.status,
                'voice': self.get_audio(),
            })
        elif self.annotations['level'] == 'Warning':
            return render_to_string('mail.html', {
                'labels': self.labels,
                'annotations': self.annotations,
                'values': self.values,
                'status': self.status,
            })
        else:
            pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._last_status or self.annotations['level'] == 'Critical':
            # Thay đổi status -> gửi mail hoặc Critical sẽ gửi mail liên tục
            print('[ALERT] Send mail')
            try:
                m = EmailMultiAlternatives(
                    f'Alert {self.fingerprint}: Status {self.status}',
                    'No text',
                    "khanhit@hocdevops.me",
                    ['thoai.phan@elofun.com'],
                )
                m.attach_alternative(self.build_mail_body(), 'text/html')
                m.send()
            except Exception as ex:
                print(f'[ALERT] Send mail failed: {ex}')
        else:
            print('[ALERT] No send mail')
