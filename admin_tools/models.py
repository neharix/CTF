from django.db import models


class Xlsxes(models.Model):
    file = models.FileField(upload_to='xlsx/')
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uploaded)