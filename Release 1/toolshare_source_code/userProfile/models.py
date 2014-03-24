from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib import messages
#from shareZone.models import // when we create a shareZone model, add here

# Create your models here.
class UserProfile(models.Model):
    url = models.URLField()
    nameFirst = models.CharField(max_length = 200)
    nameLast= models.CharField(max_length = 200)
    home_address = models.TextField()
    #phone_number = models.PhoneNumberField()
    email = models.CharField(max_length = 200)
    user = models.ForeignKey(User, unique=True)
    #shareZone = models.shareZone // reference to shareZone would go here

    def __str__(self):
        return self.user.username + ": " + self.nameFirst + " " + self.nameLast

    #insert into DB
    def insert(post):
        if not User.objects.filter(username=post['username']).exists():
            userDB = User.objects.create_user(post['username'], post['email'], post['password'])
            print("UserDB = "+ str(userDB))
            # Create the user
            UserProfile.objects.create( \
            nameFirst = post['nameFirst'], \
            nameLast=post['nameLast'], \
            home_address = post['home_address'], \
            email = post['email'], \
            user = userDB
            )
            # Assign / create the ShareZone
            print("about to create")
            mygroup, created = Group.objects.get_or_create(name=post['zipCode'])
            userDB.groups.add(mygroup)
            #messages.add_message(request,messages.INFO,"You joined a group!")
            return True

        else:
            return False

    #update the DB with user pref
    def update(post):
        pass
