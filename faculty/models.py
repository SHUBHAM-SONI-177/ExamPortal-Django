from django.db import models

# Create your models here.
class faculty(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField(primary_key=True)
    dob=models.DateField()
    address=models.CharField(max_length=300)
    password=models.CharField(max_length=1000,default='None')
    profilePic=models.ImageField(null=True)
    isActive=models.BooleanField(null=True)

    def __str__(self):
        return self.email
