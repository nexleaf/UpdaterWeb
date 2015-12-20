from django.db import models
from django.forms import ModelForm
# Create your models here.
class App (models.Model):
    name = models.CharField(max_length=100)
    package = models.CharField(max_length=100)
    ver = models.IntegerField()
    url = models.CharField(max_length=200)
    release = models.CharField(max_length=20)
    action = models.CharField(max_length=20)
    extra_urls = models.CharField(max_length=200, default="")

class User (models.Model):
    
    def save(self, *args, **kwargs):
        if not self.jitter:
            self.jitter = self.group.all()[0].jitter
        super(User, self).save(*args, **kwargs)
    name = models.CharField(max_length=100, default='')
    imei = models.CharField(max_length=20)

    # A client automatically inherits apps from its group
    group = models.ManyToManyField('Group')

    # These are apps not inherited from the group
    user_apps = models.ManyToManyField('App')

    # Inventory Information
    simid = models.CharField(max_length=40)
    phone = models.CharField(max_length=40)
    jitter = models.IntegerField(default=1)

    
class Group (models.Model):
    def save(self, *args, **kwargs):
        if self.jitter:
            users = User.objects.filter(group__name=self.name)
            for user in users:
                user.jitter = self.jitter
                user.save()
        super(Group, self).save(*args, **kwargs)
    name = models.CharField(max_length=20)
    desc = models.TextField(default='')
    apps = models.ManyToManyField('App')
    jitter = models.IntegerField(default=1)
    

class Logs (models.Model):
    imei = models.CharField(max_length=20)
    access = models.DateTimeField()
    packages = models.TextField()

class Global (models.Model):
    urls = models.CharField(max_length=200)

#class REGISTRY (models.Model):
#    imei = models.CharField(max_length=20)
#    simid = models.CharField(max_length=40)
#    phone = models.CharField(max_length=40)
#    assettag = models.CharField(max_length=40)
 
