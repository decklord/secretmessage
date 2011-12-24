from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    facebook_id = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User)

    class Meta:
        app_label = 'api'

    @staticmethod
    def get(user):
        try:
            userprofile = UserProfile.objects.get(user=user)
        except:
            userprofile = UserProfile(user=user)
            userprofile.save()

        return userprofile
    
    def set_password(self, password):
        success =  self.user.set_password(password)
        self.save()
        return success
   
    def save(self):
        super(UserProfile, self).save()
        self.user.save()

    def set(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    @property
    def username(self):
        return self.user.username

    @username.setter
    def username(self, value):
        self.user.username = value

    @property
    def first_name(self):
        return self.user.first_name

    @first_name.setter
    def first_name(self, value):
        self.user.first_name = value

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value):
        self.user.last_name = value

    @property
    def email(self):
        return self.user.email

    #user flags:
    @property
    def is_superuser(self):
        return self.user.is_superuser

    @is_superuser.setter
    def is_superuser(self, value):
        self.user.is_superuser = value

    @property
    def is_staff(self):
        return self.user.is_staff

    @is_staff.setter
    def is_staff(self, value):
        self.user.is_staff = value

    @property
    def is_active(self):
        return self.user.is_active

    @is_active.setter
    def is_active(self, value):
        self.user.is_active = value

    @email.setter
    def email(self, value):
        self.user.email = value

class Reader(Person)
	mail = models.CharField(max_length = 255)

class Writer(Person)
	mail = models.CharField(max_length = 255)

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

