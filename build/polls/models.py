from datetime import timezone, datetime
from datetime import timedelta
from django.utils import timezone
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=30)
    pub_date = models.DateField()

    def __str__(self):
        return f'{self.question_text} {self.pub_date}'


    def was_published_recently(self):
        return self.pub_date >= timezone.now().date() - timedelta(days=1)


class Choice(models.Model):
    choice_text = models.CharField(max_length=30)
    votes = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.choice_text} - {self.votes} - {self.question_id}'