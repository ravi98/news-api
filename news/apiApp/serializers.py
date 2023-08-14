from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Article, SearchTable

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=["id", "username", "email", "password","is_banned"]
        extra_kwargs={
            "password":{
                "style": {'input_type':'password'},
                "write_only":True,
                "min_length":5,
            },
            "is_banned":{
                "read_only":True,
            },
            "id":{
                "read_only":True,
            }
        }
    def create(self, validate_data):
        user_model = get_user_model()
        password=validate_data.pop("password")
        user=user_model.objects.create(**validate_data)
        user.set_password(password)
        user.save()
        return user
        

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False, # django trims whitespace from charfields by default.
    )
    
    def validate(self, attrs):
        print(attrs)
        user=authenticate(
            username=attrs.get('username'),
            password=attrs.get('password'),
        )
        print(user)
        if not user:
            msg=('Unable to authenticate the user with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user']=user
        return attrs
        

class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model=SearchTable
        fields="__all__"


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Article
        fields="__all__"


class NewsSerializer(serializers.Serializer):
    keyword=serializers.CharField(required=True, allow_blank=False)
    