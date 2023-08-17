from rest_framework import serializers
from .models import  User,FriendRequest,GroupChatRoom,GroupMessagesModel
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    # email=serializers.CharField(max_length=68,min_length=6,write_only=True)    

    default_error_messages = {
        'email': 'The email should  be valid'}

    class Meta:
        model = User
        fields = ["username",'first_name',"last_name",'email','mobile','password','profile_photo']

    def validate(self, attrs):
        email = attrs.get('email', '')
        if email.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(
        max_length=68, min_length=6, write_only=True)
    password=serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    
    class Meta:
        model=User
        fields=["email","password",'tokens',"uuid"]

    def validate(self,attr):
        email=attr.get("email",None)
        password=attr.get("password",None)
        
        if email is None:
            raise serializers.ValidationError("Email is important")
        if password is None:
            raise serializers.ValidationError("Password is complusory")
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        user=User.objects.get(email=user.email)
        return {
            'email': user.email,
            'tokens': user.tokens,
            'uuid':user.uuid,

        }
                    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["uuid","username","email","first_name","last_name","is_active"]
    
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=FriendRequest
        fields='__all__'
    
    def validate(self,attrs):
        from_friend=attrs.get("from_friend",'')
        to_friend=attrs.get("to_friend",'')
        user=User.objects.get(email=from_friend)
        print(user.friends_list)
        if from_friend == to_friend:
            raise serializers.ValidationError({'recipient': 'You cannot send a friend request to yourself.'})
        if user.friends_list.filter(email=to_friend):
            raise serializers.ValidationError({"error":"User is already in you're friend list"})
        return attrs
    def create(self,validated_data):
        return FriendRequest.objects.create(**validated_data)
    
class AcceptFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model=FriendRequest
        fields="__all__"

class GroupChatSerializer(serializers.ModelSerializer):
    # image=serializers.FileField()
    class Meta:
        model=GroupChatRoom
        fields=['name','image','users','admin_user']


    def create(self, validated_data):
        print(validated_data,"ll")
        admin_users=validated_data.pop('admin_user')
        user_data=validated_data.pop('users')
        group_chat_room = GroupChatRoom(**validated_data)
        group_chat_room.save()
        if len(user_data)!=0:
            print("kkk")
            for user in user_data:
                print(user)
                group_chat_room.users.add(user)
        if len(admin_users)!=0:
            for admin in admin_users:
                group_chat_room.admin_user.add(admin)
        group_chat_room.admin_user.add(validated_data.get('created_by'))
        group_chat_room.users.add(validated_data.get('created_by'))
        group_chat_room.save()
        return group_chat_room
    
class GroupChatListSerializer(serializers.ModelSerializer):
    admin_user=serializers.SerializerMethodField('get_admin_user')
    users=serializers.SerializerMethodField('get_users')
    created_by=serializers.SerializerMethodField('get_created_by')
    # image=serializers.FileField()
    class Meta:
        model=GroupChatRoom
        fields=['uuid','name','image','users','admin_user','created_at','created_by']
        # return model
    @staticmethod
    def get_admin_user(obj):
        try:
            return list(obj.admin_user.values_list("email", flat=True))
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def get_users(obj):
        try:
            return list(obj.users.values_list("email", flat=True))
        except Exception as e:
                print(e)
                return None
    @staticmethod
    def get_created_by(obj):
        try:
            return obj.created_by.email
        except Exception as e:
                print(e)
                return None

