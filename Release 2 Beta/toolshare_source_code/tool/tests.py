"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from tool.models import Tool

def createTool(
		name,
        description, 
        ownerID,
        currentOwnerID,
        availability,
        quantityCurr, 
        quantityMax,  
        specialInstructions):
	Tool.objects.create(
		name = name,
        description = description, 
        ownerID = ownerID,
        currentOwnerID = currentOwnerID,
        availability = availability,
        quantityCurr = quantityCurr, 
        quantityMax = quantityMax,  
        specialInstructions = specialInstructions)

class ToolModelTests(TestCase):
    def test_create_tool(self):
        """
        Tests that tools are correctly created in the database.
        """
        createTool("hammer", "a fine steel hammer", 1, 1, True, 1, 1, "be careful")
        self.assertEqual(Tool.objects.get(ownerID = 1).name, "hammer")