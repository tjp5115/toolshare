from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from shareZone.models import ShareZone


# A reservation represents a date range that a tool is unable to be borrowed
# This can happen for two reasons:
#   1. The owner wishes to use it for that time range
#   2. Somebody has reserved the tool and the owner has agreed
class Reservation(models.Model):
    dateStart = models.DateField()
    dateEnd   = models.DateField()

    # Returns whether a given day is reserved or not
    # This never needs to be called, but the logic is good to have
    def isDateReserved(self, day):
        return day >= self.dateStart and day <= self.dateEnd

    def __str__(self):
        return  "Reserved from " + str(self.dateStart) + " to " + str(self.dateEnd)

# A tool represents a user's tool and all information needed to borrow it.
# It is aware of its current and original owner
# "status" is from the perspective of the tool's owner
class Tool(models.Model):
    name                = models.CharField(max_length = 200)
    description         = models.CharField(max_length = 300)
    status              = models.CharField(max_length = 100, default = 'At home')
    ownerID             = models.IntegerField()
    currentOwnerID      = models.IntegerField()
    pickupArrangements  = models.CharField(max_length = 300)
    reservations        = models.ManyToManyField(Reservation)
    shareZone           = models.ForeignKey(ShareZone)
    coordinator         = models.ForeignKey(User, default = None, blank = True, null = True, on_delete=models.SET_NULL)
    numBorrowed         = models.IntegerField(default = 0)

    # Returns a string represntation of the tool
    def __str__(self):
        return self.name# + ": " + self.description 
    
    # Add a reservation to the Tool's list of reservations
    # dateStart: (date object) the first day of the reservation
    # dateEnd:   (date object) the last day of the reservation
    # precondition: the reservation must not conflict with existing ones
    def addReservation(self, dateStart, dateEnd):
        # If the dates are backward, fix them
        if dateStart > dateEnd:
            dateStart, dateEnd = dateEnd, dateStart

        # The tool better be available!
        assert not self.isDateRangeReserved(dateStart, dateEnd),\
        "The tool cannot be reserved for " + str(dateStart) + " through " + \
        str(dateEnd) + " because there is a conflicting reservation"    

        reservation = Reservation(dateStart = dateStart, dateEnd = dateEnd)
        reservation.save()
        self.reservations.add(reservation)
        self.save()

    # Returns true if the tool has a future reservation
    def hasFutureReservation(self):
        return self.reservations.all().filter(
            dateEnd__gte = timezone.datetime.today().date()
        ).count() > 0

    # Returns whether the given day is reserved already
    def isDayReserved(self, day):
        return self.reservations.all().filter(
            dateStart__lte = day
        ).filter(
            dateEnd__gte = day
        ).count() > 0

    # Returns whether the given date range contains a reservation
    def isDateRangeReserved(self, start, end):
        # If the start is greater than a reservation's start date
        # and less than a reservation's end date, it conflicts
        # The same principle applies to the end date given
        # The third case is the start is less than the beginning
        # of the reservation, and the end is past the end
        return self.reservations.all().filter(
            dateStart__lte = start
        ).filter(
            dateEnd__gte = start
        ).count() + self.reservations.all().filter(
            dateStart__lte = end
        ).filter(
            dateEnd__gte = end
        ).count() + self.reservations.all().filter(
            dateStart__gte = start
        ).filter(
            dateEnd__lte = end
        ).count() > 0

    # Returns a list of all reserved days is json format, for use with datepicker
    def getReservedDays(self):
        dthandler = lambda obj: obj.isoformat()
        dates = []
        for reservation in self.reservations.all():
            for date in range(int ((reservation.dateEnd - reservation.dateStart).days) + 1):
                dates.append(reservation.dateStart + timezone.timedelta(date))

        import json
        print(json.dumps(dates, default=dthandler))
        return json.dumps(dates, default=dthandler)

    # Deletes a reservation with both dateStart and dateEnd, if it exists
    def deleteReservationByRange(self, dateStart, dateEnd):
        self.reservations.all().filter(
                dateStart = dateStart
            ).filter(
                dateEnd = dateEnd
            ).delete()

    # Deletes a reservation that contains a given date, if it exists
    def deleteReservationByDay(self, date):
        self.reservations.all().filter(
                dateStart__lte = date
            ).filter(
                dateEnd__gte = date
            ).delete()

    # Rejected all pending notifications associated with this tool
    def deleteNotifications(self):
        assert not self.hasFutureReservation()
        from notifications.models import Notification
        for notification in Notification.objects.all().filter(
                toolID = self.id
            ).filter(
                status = 'pending'
            ):
            notification.setRejected("The tool's owner removed this tool from ToolShare.")

    # Return the first available today the tool may be reserved
    # This is disgusting
    def getFirstAvailableDate(self):
        # Grab the first reservation end greater than or equal to today
        date = timezone.datetime.today().date()

        # Loop until we find a day that isn't reserved
        while self.isDayReserved(date):

            # Find the last day of the next reservation
            newDate = self.reservations.all().filter(
                dateEnd__gte = date
            ).order_by('dateEnd')[0:1]

            # If it's not empty, advance it to the day after the next
            # reservation's last day. Else, return the day after
            if newDate != []:
                date = newDate[0].dateEnd + timezone.timedelta(days = 1)
            else:
                return date + timezone.timedelta(days = 1)

        # If we never entered the loop, return today
        return date

    # Returns the current status of the tool, for use in displaying in
    # tables of tools. A tool is either loaned out, at home, or in a shed
    def getStatus(self):
        if self.ownerID != self.currentOwnerID:
            return "Loaned to " + str(User.objects.get(id = self.currentOwnerID).get_profile())
        else:
            if self.coordinator == None:
                return "At home"
            else:
                if self.coordinator == self.ownerID:
                    return "In my shed"
                else:
                    return "In " + str(self.coordinator.get_profile()) + "'s shed"

    def borrow(self):
        """
        is this necessary?
        """ 
        pass

    # Lends the tool to the User indicated by receiverID
    def lend(self, receiverID):
        self.currentOwnerID = receiverID
        self.save()

    # Increases the borrowed counter by one
    def incrementBorrowed(self):
        self.numBorrowed += 1
        self.save()

    # Updates the tool indicated by toolID with the information in the request object
    def update(request, toolID):
        #print("THE USER IS:")
        #print(request.user.id)
        #print(UserProfile.objects.all().filter(user = request.user.id)[0])
        tool = Tool.objects.get(pk = toolID)
        tool.name = request.POST['name']
        tool.description = request.POST['description'] 
            #picture =request.POST['name'],
            #status =request.POST['name'],
        tool.save()

    def deleteTool(request, toolID):
        tool = Tool.objects.get(pk = toolID)
        # Check if the current owner is the original owner 
        # and does not have a future reservation, if so a tool can be deleted
        if tool.hasFutureReservation():
            return 2
        elif tool.currentOwnerID != tool.ownerID:
            return 3
        elif tool.isLastShedTool():
            return 4
        else:
            tool.deleteNotifications()
            tool.delete()
            return 1

    #if it is the last shed tool, it will return true 
    #used for delete -- can not delete the last tool
    def isLastShedTool(self):
       print("count = " + str(self.getOwner().tool_set.all().filter(ownerID=self.ownerID).count()) )
       return self.getOwner().tool_set.all().filter(ownerID=self.ownerID).count() == 1

    # Returns the tool to its original owner
    def returnToOwner(self):
        self.currentOwnerID = self.ownerID
        self.save()

    # Gets the User Profile of the tool's owner
    def getOwner(self):
        return User.objects.get(pk=self.ownerID)

    # Gets the User Profile of the tool's owner
    def getCurrentOwner(self):
        return User.objects.get(pk=self.currentOwnerID)

    # Inserts a tool into the database using the information in the request object
    def insert(request):
        #print("THE USER IS:")
        #print(request.user.id)
        #print(UserProfile.objects.all().filter(user = request.user.id)[0])
        
        from userProfile.models import UserProfile

        owner = UserProfile.objects.all().get(user = request.user.id)

        Tool.objects.create(
            name = request.POST['name'], 
            description = request.POST['description'], 
            #picture =request.POST['name'],
            #status =request.POST['name'],
            ownerID = request.user.id,
            currentOwnerID = request.user.id,
            pickupArrangements = owner.home_address,
            shareZone = owner.shareZone
        ) 

    ########################################################################
    ################### Coordinator calls ##################################
    ########################################################################

    # Adds the tool to the coordinators shed (coordinator is a User object)
    def addToShed(self, coordinator):
        self.coordinator = coordinator
        self.save()

    # Remove the tool from its shed
    # Postconditions: all relevant notifications's receiverID are changed to
    # the tool owner's ID, and the tool no longer has a coordinator
    def removeFromShed(self):
        from notifications.models import Notification
        for notification in Notification.objects.all().filter(toolID = self.pk):
            notification.receiverID = self.ownerID
            notification.save()
        
        self.coordinator = None
        self.save()

    # Returns true if the tool is currently in a shed
    def isInShed(self):
        return self.coordinator != None

    # Returns the tool's shed coordinator (User), or None if not in a shed
    def getCoordinator(self):
        return self.coordinator

    # Sets tool's shed coordinator (userProfile is a UserProfile, not a user)
    def setCoordinatorProfile(self, userProfile):
        from userProfile.models import UserProfile
        assert isinstance(userProfile, UserProfile)
        self.coordinator = userProfile.user
        self.save()

    # Sets tool's shed coordinator (user is a user, not a UserProfile)
    def setCoordinator(self, user):
        assert isinstance(user, User)
        self.coordinator = user
        self.save()

    # Returns the User Profile of the shed's coordinator, or None if not in a shed
    def getCoordinatorProfile(self):
        if self.coordinator != None:
            return self.coordinator.get_profile()
        else:
            return None