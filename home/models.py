from django.db import models

class Person(models.Model)
	mail = models.CharField(max_length = 255)

class Reader(Person)

class Writer(Person)

class Message(models.Model):
	
	description = models.TextField()
	message = models.TextField()
	reveal_on = models.DateTimeField()
	admin = models.ForeignKey(Writer)
	opened = models.BooleanField()
	readed = models.BooleanField()

	def open():
		this.opened = True
		this.save()

	def read():
		this.read = True
		this.save()

