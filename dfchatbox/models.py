from django.db import models

class Procedure(models.Model):
    nameENG = models.CharField(max_length=500)
    nameSLO = models.CharField(max_length=500)
    lemma = models.CharField(max_length=500,default=None,null=True)
    procedure_id = models.CharField(max_length=10)
