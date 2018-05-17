from django.db import models

class Procedure(models.Model):
    nameENG = models.CharField(max_length=500)
    nameSLO = models.CharField(max_length=500)
    procedure_id = models.CharField(max_length=10)
