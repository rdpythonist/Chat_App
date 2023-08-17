from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .models import Message,ChatRoom,User,FriendRequest,GroupChatRoom,GroupMessagesModel
from .serializers import RegisterSerializer,LoginSerializer,UserSerializer,GroupChatListSerializer,GroupChatSerializer,AcceptFriendSerializer,FriendRequestSerializer
from rest_framework import generics ,response,status,views,serializers
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens  import RefreshToken
from rest_framework.permissions import IsAdminUser, IsAuthenticated
import json

# Create your views here.


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        serializer.save()
        user=User.objects.get(email=serializer.data['email'])
        token = RefreshToken.for_user(user).access_token
        # current_site = get_current_site(request).domain
        # relativeLink = reverse('email-verify')
        # absurl = 'https://'+current_site+relativeLink+"?token="+str(token)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class GetProfile(views.APIView):
    serializer_class=UserSerializer
    permission_classes=(IsAuthenticated,)
    def get_object(self, uuid):
        try:
            return User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            raise serializers.ValidationError("No User")
    def get(self, request, uuid, format=None):
        snippet = self.get_object(uuid)
        serializer = UserSerializer(snippet)
        return response.Response(serializer.data)

class FriendRequestView(views.APIView):
    serializer_class=FriendRequestSerializer
    # permission_classes=(IsAuthenticated,)
    def get_object(self,uuid):
        try:
            return User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            raise serializers.ValidationError("No User")
    def post(self,request):
        serializers=FriendRequestSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return response.Response(serializers.data, status=status.HTTP_200_OK)
        return response.Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendRequestAcceptView(views.APIView):
    # permission_classes = (IsAuthenticated,)

    def get_object(self,uuid):
        try:
            return FriendRequest.objects.get(uuid=uuid)
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError("No friend request")

    def get(self, request, uuid):
        friendrequest = self.get_object(uuid)
        serializer = AcceptFriendSerializer(friendrequest)
        return response.Response(serializer.data)

    def post(self, request, uuid):
        snippet = self.get_object(uuid)
        data=snippet.accept(request.data['status'])
        if data is True:
            return response.Response({"success":"Friend request accepted"}, status=status.HTTP_200_OK)
        else:
            return response.Response({"success":"Friend request rejected"}, status=status.HTTP_400_BAD_REQUEST)

class GroupChatCreateView(generics.GenericAPIView):
    serializer_class = GroupChatSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request):
        print(request.data)
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save(created_by=request.user)
            return response.Response(serializers.data, status=status.HTTP_200_OK)
        return response.Response({"error":"Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class GroupListView(generics.GenericAPIView):
    serializer_class=GroupChatListSerializer
    permission_classes=[IsAuthenticated]

    def get(self,request):
        user=User.objects.get(email=request.user)
        groups=GroupChatRoom.objects.filter(created_by=user)
        serializers=self.serializer_class(groups,many=True)
        return response.Response(serializers.data, status=status.HTTP_200_OK)
# User=get_user_model()

# def hello(request):
#     return HttpResponse("Hello")

def index(request):
    users=User.objects.exclude(username=request.user.username)
    print(users)
    return render(request, "chats/index.html",{"users":users})

def group(request):
    group=GroupChatRoom.objects.filter(users=request.user)
    group_messages=GroupMessagesModel.objects.filter(room__in=group).filter(read=False)
    unread_messages_by_group = {}

    for message in group_messages:
        groups = message.room
        if groups not in unread_messages_by_group:
            unread_messages_by_group[groups] = 0
        unread_messages_by_group[groups] += 1
    print(unread_messages_by_group)
    return render(request, "chats/group.html",{"group":group,"unread_messages":unread_messages_by_group})

def room(request, email):
    user_obj=User.objects.get(email=email)
    user_objs=User.objects.get(email=email).id
    users=User.objects.exclude(email=request.user)
    if request.user.id >user_objs:
        thread_name = f'chat_{request.user.id}-{user_obj.id}'
    else:
        thread_name = f'chat_{user_obj.id}-{request.user.id}'
    room = ChatRoom.objects.get(name=thread_name)
    messages_objs=Message.objects.filter(room=room)
    return render(request, "chats/room.html", {"user": user_obj.username,"users":users,"user_id":user_objs,"messages_obj":messages_objs})

def grouproom(request,group_name):
    grouprooms = GroupChatRoom.objects.get(name=group_name)
    group_messages=GroupMessagesModel.objects.filter(room=grouprooms)
    return render(request, "chats/groupchatroom.html", {"chatgroup": grouprooms,"group_message":group_messages})