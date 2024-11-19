from email.mime.image import MIMEImage
from urllib.parse import urlparse, parse_qs

import requests
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from requests import request
from demo.settings import TOKEN_GRAFANA

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
    url = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _last_status = None

    def set_status(self, next_status):
        if next_status != self.status:
            self._last_status = self.status
        self.status = next_status

    def __str__(self):
        return f'{self.fingerprint}: {self.status}'


    def get_grafana_image(self):
        parsed_url = urlparse(self.url)
        query_params = parse_qs(parsed_url.query)

        dashboard_uid = parsed_url.path.split('/')[-1]
        panel_id = query_params.get("viewPanel", [1])[0]

        grafana_base = f"{parsed_url.scheme}://{parsed_url.netloc}"
        grafana_url = f"{grafana_base}/render/d-solo/{dashboard_uid}/dashboard?{parsed_url.query}"
        headers = {
            'Authorization': f'Bearer {TOKEN_GRAFANA}'
        }
        params = {
            'panelId': panel_id,
            'width': 1000,
            'height': 500,
            'timeout': 30,
            'orgId': query_params.get("orgId", [1])[0],
        }
        try:
            response = requests.get(grafana_url, headers=headers, params=params, stream=True)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Failed to get Grafana image: {str(e)}")
            print(f"Attempted URL: {grafana_url}")
            print(f"Response status code: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
            raise Exception(f"Failed to get Grafana image: {str(e)}")

    def build_mail_body(self):
        try:
            image_content = self.get_grafana_image()
            image_path = '/tmp/alert_image.png'
            with open(image_path, 'wb') as f:
                f.write(image_content)
        except Exception as e:
            print(f"Error fetching image: {e}")
            image_path = None
        if self.annotations['level'] == 'Critical':
            html_body = render_to_string('mail.html', {
                'labels': self.labels,
                'annotations': self.annotations,
                'values': self.values,
                'status': self.status,
                'url': self.url,
                'createdAt': self.created_at,
                # 'voice': self.get_audio(),
            })
            return html_body, image_path

        elif self.annotations['level'] == 'Warning':
            html_body = render_to_string('mail.html', {
                'labels': self.labels,
                'annotations': self.annotations,
                'values': self.values,
                'status': self.status,
                'url': self.url,
                'createdAt': self.created_at,
            })
            return html_body, image_path
        else:
            pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._last_status or self.annotations['level'] == 'Critical':
            # Thay đổi status -> gửi mail hoặc Critical sẽ gửi mail liên tục
            print('[ALERT] Send mail')
            try:
                html_body, image_path = self.build_mail_body()
                m = EmailMultiAlternatives(
                    f'Alert {self.fingerprint}: Status {self.status}',
                    'No text',
                    "khanhit@hocdevops.me",
                    ['thoai.phan@elofun.com'],
                )
                m.attach_alternative(html_body, 'text/html')
                if image_path:
                    with open(image_path, 'rb') as img:
                        image = MIMEImage(img.read())
                        image.add_header('Content-ID', '<alert_image>')
                        image.add_header('Content-Disposition', 'inline', filename='alert_image.png')
                        m.attach(image)
                m.send()
            except Exception as ex:
                print(f'[ALERT] Send mail failed: {ex}')
        else:
            print('[ALERT] No send mail')
