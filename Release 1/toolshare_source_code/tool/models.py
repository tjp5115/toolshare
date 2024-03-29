from django.db import models
from userProfile.models import UserProfile

# Create your models here.
class Tool(models.Model):
    name= models.CharField(max_length = 200)
    description = models.CharField(max_length = 300)
    #picture = models.CharField(max_length = 100)
    status = models.CharField(max_length = 100)
    ownerID = models.IntegerField()
    currentOwnerID = models.IntegerField()
    availability = models.BooleanField(False) #should inital be false?
    pickupArrangements = models.CharField(max_length = 300)
    quantityCurr= models.IntegerField()
    quantityMax= models.IntegerField()
    specialInstructions = models.CharField(max_length = 300)

    def __str__(self):
        return self.name + ": " + self.description + ". available: " + str(self.availability)
    
    def borrow():
        pass

    def lend():
        pass

    def update(request,toolId):
        #print("THE USER IS:")
        #print(request.user.id)
        #print(UserProfile.objects.all().filter(user = request.user.id)[0])
        tool = Tool.objects.get(pk=toolId)
        tool.name = request.POST['name']
        tool.description = request.POST['description'] 
            #picture =request.POST['name'],
            #status =request.POST['name'],
            #availability = request.POST['name'],
            #pickupArrangements = request.POST[''],
        if int(request.POST['quantityMax']) <=0:
            models.Tool.objects.delete(pk=toolId)
        tool.quantityMax = int(request.POST['quantityMax'])  
        tool.specialInstructions = request.POST['specialInstructions']            
        tool.save()


    def returnToOwner():
        #currentOwner = owner
        pass

    def insert(request):
        #print("THE USER IS:")
        #print(request.user.id)
        #print(UserProfile.objects.all().filter(user = request.user.id)[0])
        Tool.objects.create(
            name = request.POST['name'], 
            description = request.POST['description'], 
            #picture =request.POST['name'],
            #status =request.POST['name'],
            ownerID = request.user.id,
            currentOwnerID = request.user.id,
            #availability = request.POST['name'],
            #pickupArrangements = request.POST[''],
            quantityCurr = request.POST['quantityMax'], 
            quantityMax = request.POST['quantityMax'],  
            specialInstructions = request.POST['specialInstructions']  
         ) 
