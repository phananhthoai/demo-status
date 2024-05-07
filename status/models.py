from django.db import models


class Servers(models.Model):
    server = models.CharField(max_length=30)
    ip = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.server} - {self.ip}'


class Status(models.Model):
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=30)
    server = models.ForeignKey(Servers, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.status} - {self.updated_at} - {self.content}'


class Alert(models.Model):
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    describe = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    server = models.ForeignKey(Servers, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.status.name} - {self.updated_at} - {self.describe}'