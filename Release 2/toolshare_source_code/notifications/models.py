from django.db import models
from django.utils import timezone
from tool.models import Tool
from django.contrib.auth.models import User

"""
Represents a notification pertaining to borrowing a tool.

status: a notification may have eight states:
    'pending'               : the request is awaiting reply
    'accepted'              : the request has been approved
    'rejected'              : the request have been rejected
    'waiting'               : the request has been accepted, and is now 
                              'waiting' for the day that it becomes active
    'active'                : the accepted request's time has come - the tool
                              has officially changed hands to the borrower. it 
                              is now 'waiting' for its active state to finish.
                              note that the borrower may return at this point
    'awaitingReturn'        : the tool's lending period has finished, and it is
                              now time for the borrower to return the tool
    'awaitingConfirmation'  : the bororwer has marked the tool as returned, and
                              it is now time for the lender to confirm that
    'archived'              : the request has completed its lifecycle,
                              remaining in the database for future reference 
                              (if desired + implemented)

description     : the notification's description ('I need to fix my door')
senderID        : the primary key of the sending user (the borrower)
receiverID      : the primary key of the receiving user (the lender)
toolID          : the primary key of the tool in question
timeStart       : the date that the request will start
timeEnd         : the date that the request will end
"""
class Notification(models.Model):
    status      = models.CharField(max_length = 30)
    description = models.CharField(max_length = 400)
    senderID    = models.IntegerField()
    receiverID  = models.IntegerField()
    toolID      = models.IntegerField()
    timeStart   = models.DateField()
    timeEnd     = models.DateField()

    def __str__(self):
        from userProfile.models import UserProfile
        sender = UserProfile.objects.get(user=self.senderID)
        sender = sender.nameFirst + " " + sender.nameLast
        receiver = UserProfile.objects.get(user=self.receiverID)
        receiver = receiver.nameFirst + " " + receiver.nameLast

        return "Type: " + self.status + ", description: " + \
            self.description + ", sender: " + sender + \
                ", receiver: " + receiver + ", tool: " + \
                    str(Tool.objects.get(pk=self.toolID))

    # Inserts a notification into the database using the information in the request object
    def insert(request,toolID,receiverID):

        # Converts the MM/DD/YYYY format from datepicker to Django's required
        # YYYY-MM-DD format    
        def fixFormat(date):
            toks = date.split('/')
            return toks[2] + '-' + toks[0] + '-' + toks[1]

        notification = Notification.objects.create(
            status      = 'pending', 
            description = request.POST['reason'], 
            senderID    = request.user.id,
            timeStart   = fixFormat(request.POST['timeStart']),
            timeEnd     = fixFormat(request.POST['timeEnd']),
            receiverID  = receiverID,
            toolID      = toolID,
        )

        # Swap dates if necessary (only happens if javascript is disabled)
        if notification.timeStart > notification.timeEnd:
            notification.timeStart, notification.timeEnd =\
            notification.timeEnd,   notification.timeStart
            notification.save()

        # We must check that the notification doesn't conflict with current reservations
        # If so, delete it
        if notification.isConflict():
            notification.delete()
            return False

        # If the tool is in a shed or the user is reserving for himself, 
        # automatically accept the request
        if Tool.objects.get(pk = toolID).isInShed() or \
            request.user.id == receiverID:
            notification.setAccepted()

        return True


    def getDateRange(self):
        start = str(self.timeStart)
        start = start.split('-')
        end = str(self.timeEnd)
        end = end.split('-')
        return str(start[1])+'/'+str(start[2])+'/'+str(start[0]) +" - "+str(end[1])+'/'+str(end[2])+'/'+str(end[0])
    
    # get tool for the notification
    def getTool(self):
        return Tool.objects.get(pk=self.toolID).name

    # get tool owner for the notification
    def getOwner(self):
        return User.objects.get(pk=self.receiverID).get_profile().nameFirst + " " + \
               User.objects.get(pk=self.receiverID).get_profile().nameLast

    # get tool borrower for the notification
    def getSender(self):
        return User.objects.get(pk=self.senderID).get_profile().nameFirst + " " + \
               User.objects.get(pk=self.senderID).get_profile().nameLast

    # Returns whether the notification conflicts with a reservation 
    # on the tool in question
    def isConflict(self):
        return Tool.objects.get(pk=self.toolID).isDateRangeReserved(self.timeStart, self.timeEnd)

    # Accepts a notification
    # Status must be pending beforehand
    # precondition: not isConflict
    def setAccepted(self):
        assert self.status == 'pending'
        assert not self.isConflict(), "Cannot accept the notification because it conflicts with a reservation"

        # It's time to actually reserve the tool
        Tool.objects.get(pk=self.toolID).addReservation(self.timeStart, self.timeEnd)

        self.status = 'accepted'
        self.save()

        from userProfile.models import UserProfile
        # Increment the borrow/loans counters of the associated users/tools
        Tool.objects.get(pk = self.toolID).incrementBorrowed()
        UserProfile.objects.get(user = self.senderID).incrementBorrows()
        UserProfile.objects.get(user = self.receiverID).incrementLoans()

        # Reject conflicting notifications. Note! WE SHOULD WARN THE USER ABOUT THIS
        for notification in Notification.objects.all().filter(
                toolID = self.toolID
            ).filter(status = 'pending'):

            if notification.isConflict():
                notification.setRejected("The tool's owner accepted another " +\
                "request which conflicted with yours.")

        # Now that the reservation is made, go directly into the waiting state
        self.setWaiting()

    # Rejects a notification
    # Status must be pending beforehand
    def setRejected(self,reason):
        assert self.status == 'pending'
        self.status = 'rejected'
        self.description = str(reason)
        self.save()
    
    # Accepts a notification
    # Status must be accepted beforehand
    def setWaiting(self):
        assert self.status == 'accepted'
        self.status = 'waiting'
        self.save()

    # Activates a notification, lending a tool to the borrower
    # Preconditions: the notification's start date >= today's date
    #                the notification's end   date <  today's date
    #                notification's status is accepted or waiting
    # Postcondition: the tool has been lent to the borrower
    def setActive(self):
        assert self.status == 'accepted' or self.status == 'waiting'
        assert self.timeStart <= timezone.datetime.today().date()
        self.status = 'active'
        Tool.objects.get(pk=self.toolID).lend(self.senderID)
        self.save()

    # Marks a notification as awaiting return
    # Precondition: the notification's end date >= today's date
    # Status must be active beforehand
    def setAwaitingReturn(self):
        assert self.status == 'active' or self.status == 'awaitingConfirmation'
        assert self.timeEnd <= timezone.datetime.today().date()
        self.status = 'awaitingReturn'

        # If tool is reserved by its owner, auto-archive
        if self.senderID == self.receiverID:
            self.status = 'awaitingConfirmation'
            self.save()
            self.setArchived()

        self.save()

    # Marks a notification as awaiting confirmation
    # Status must be awaitingReturn or active beforehand
    def setAwaitingConfirmation(self):
        assert self.status == 'awaitingReturn' or self.status == 'active'
        self.status = 'awaitingConfirmation'
        self.save()

        # If tool is reserved by its owner, auto-archive
        if self.senderID == self.receiverID:
            self.setArchived()

    # Returns the tool to the borrower, as well as archiving the
    # notification for statistic purposes
    # Postcondition: the tool is returned to the lender
    def setArchived(self):
        assert self.status == 'awaitingConfirmation' or self.status == 'rejected'
        # If the tool was lent out, return it and delete the reservation
        if self.status == 'awaitingConfirmation':
            Tool.objects.get(pk=self.toolID).deleteReservationByDay(self.timeStart)
            Tool.objects.get(pk=self.toolID).returnToOwner()
        self.status = 'archived'
        self.save()

    # Checks if the notification becomes active, awaitingReturn, or expire today
    # Postcondition: if the notification should become active, awaitingReturn,
    #                or expire, setActive(), setAwaitingReturn(), or
    #                setRejected() is called. otherwise, nothing happens
    def checkForChanges(self):
        print("entered checkForChanges")
        # Both accepted and waiting status notifications may become active
        if self.status == 'accepted' or self.status == 'waiting':
            if self.timeStart <= timezone.datetime.today().date():
                print("set active passed")
                self.setActive()

        # Only active notifications can become setAwaitingReturn
        if self.status == 'active':
            if self.timeEnd <= timezone.datetime.today().date():
                print("set awaitingReturn passed")
                self.setAwaitingReturn()

        # This checks for expired notifications
        if self.status == 'pending':
            if self.timeEnd <= timezone.datetime.today().date():
                self.setRejected("The tool's owner didn't respond in time to accept your request.")

    # Allows a waiting request to be canceled
    # Request must be in waiting state
    def cancelWaitingRequest(self):
        assert self.status == 'waiting'

        # Delete the reservation associated with this request
        # Filter twice just in case the reservation didn't exist
        Tool.objects.get(
                pk = self.toolID
            ).reservations.filter(
                dateStart = self.timeStart
            ).filter(
                dateEnd = self.timeEnd
            ).delete()

        # Delete this notification
        self.delete()

    # Allows a pending request to be canceled
    # Request must be in pending state
    def cancelPendingRequest(self):
        assert self.status == 'pending'

        # Delete this notification
        self.delete()