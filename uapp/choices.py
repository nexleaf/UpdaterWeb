from uapp.models import App, User, Group, Logs#, REGISTRY
g = Group.objects.all()
CHOICES = ()
l=1
for i in g:
	CHOICES = CHOICES + ((l,i.name,),)
	l=l+1

APP_CHOICES = ((1,"lol",),(2,"hi",),(3,"pop",))