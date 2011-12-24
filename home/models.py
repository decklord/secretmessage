from django.db import models

class User(models.Model):
	mail = models.CharField(max_length = 255)

class Message(models.Model):
	
	description = models.TextField()
	message = models.TextField()
	reveal_on = models.DateTimeField()
	sender = models.ForeignKey(User)
	opened = models.BooleanField()
	readed = models.BooleanField()

	def open():
		this.opened = True
		this.save()

	def read():
		this.read = True
		this.save()