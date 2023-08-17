from django.db import models
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin,BaseUserManager)
from rest_framework_simplejwt.tokens import RefreshToken
import io
from django.core.files.storage import default_storage as storage
from PIL import Image
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        # username = self.model.normalize_username(username)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username=models.CharField(max_length=50,blank=True, null=True)
    first_name=models.CharField(max_length=50,blank=True, null=True)
    last_name=models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    mobile=models.CharField(max_length=12,blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_online=models.BooleanField(default=False)
    created_by=models.CharField(max_length=50,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    profile_photo=models.ImageField(upload_to='profile_pictures/')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    friends_list=models.ManyToManyField('self',blank=True)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    # REQUIRED_FIELDS = ['email']
    objects=UserManager()
    def __str__(self):
        return self.email
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
class FriendRequest(models.Model):
    CHOICE_TYPE=(("PENDING","pending"),
                 ("ACCEPTED","accepted"),
                 ("DELETED","deleted"))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    from_friend=models.ForeignKey(User,on_delete=models.CASCADE,related_name='from_friend')
    to_friend=models.ForeignKey(User,on_delete=models.CASCADE,related_name='to_friend')
    status=models.CharField(max_length=20,choices=CHOICE_TYPE,default='pending')

    def accept(self,status):
        if status=='ACCEPTED':
            self.status='ACCEPTED'
            self.from_friend.friends_list.add(self.to_friend)
            self.to_friend.friends_list.add(self.from_friend)
            self.save()
            return True
        else:
            return False
    

class ChatRoom(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=100,null=False)
    users=models.ManyToManyField(User,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


    
class Message(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False)
    from_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender_message')
    messages=models.TextField()
    to_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='reciever_message')
    room=models.ForeignKey(ChatRoom,on_delete=models.CASCADE)
    timesatmp=models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.from_user)+ '-' +str(self.to_user)
    
class GroupChatRoom(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False)
    image=models.ImageField(upload_to='group_image',null=True,blank=True)
    name=models.CharField(max_length=100,null=False)
    users=models.ManyToManyField(User,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    admin_user=models.ManyToManyField(User,blank=True,related_name='admins')
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='creator')

    def __str__(self):
        return self.name


    
class GroupMessagesModel(models.Model):
    uuid=models.UUIDField(default=uuid.uuid4,editable=False)
    from_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='from_user')
    messages=models.TextField()
    room=models.ForeignKey(GroupChatRoom,on_delete=models.CASCADE)
    timesatmp=models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.from_user)