# Create your models here.
from django.db import models



class HospitalMaster(models.Model):
    hospital = models.CharField(max_length=10)
    speciality = models.CharField(max_length=100)
    spltycode = models.CharField(max_length=20, unique=True, primary_key=True)
    category = models.CharField(max_length=50)
    subcatg = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.spltycode} - {self.speciality}"

class HospitalVisit(models.Model):
    rslno = models.BigIntegerField(primary_key=True)
    thevalue = models.IntegerField()
    thecode = models.CharField(max_length=20)
    speciality = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    themnth = models.IntegerField()
    theyr = models.IntegerField()
    hospital = models.CharField(max_length=10)
    theday = models.IntegerField()
    spltycode = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    subcatg = models.CharField(max_length=50)
    hospital_master = models.ForeignKey(
        HospitalMaster,
        to_field='spltycode',
        on_delete=models.CASCADE,
        related_name='visits',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.speciality} ({self.thecode}) - {self.rslno}"

