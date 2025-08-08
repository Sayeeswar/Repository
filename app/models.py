# Create your models here.
from django.db import models

class Author(models.Model):
    author_name = models.CharField(max_length=100, default="Unknown Author")
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.author_name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True, blank=True)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    summary = models.TextField(blank=True)

    def __str__(self):
        return self.title

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

