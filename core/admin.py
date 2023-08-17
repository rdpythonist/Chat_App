from django.contrib import admin
from .models import User,FriendRequest,GroupChatRoom,GroupMessagesModel
# Register your models here.


admin.site.register(User)
admin.site.register(FriendRequest)
admin.site.register(GroupChatRoom)
admin.site.register(GroupMessagesModel)
# admin.site.register(ChatRoom)
# admin.site.register(Message)
