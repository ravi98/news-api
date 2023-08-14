import requests
import pytz

from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.utils.dateparse import parse_datetime
from .models import Article, SearchTable, User
from .forms import SearchForm

from rest_framework import (
    generics,
    viewsets,
    mixins,
    status
)

from news.settings import API_KEY
from .serializers import UserSerializer, LoginSerializer, NewsSerializer, ArticleSerializer, SearchSerializer

from datetime import datetime, timedelta
# Create your views here.


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class=UserSerializer
    
    def post(self, request):
        user_serializer=self.serializer_class(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return redirect('user-login')

class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        logout(request)
        return redirect('user-login')


class AdminDash(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = UserSerializer
    
    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        users = self.serializer_class(users, many=True)
        
        return render(request, "apiApp/admin-dash.html", {'users':users.data})
    
    def post(self, request):
        ban_id=request.POST.get('ban-id')
        unban_id=request.POST.get('un-ban-id')

        if ban_id:
            user=User.objects.get(username=ban_id)
            user.is_banned=True
            user.save()
        elif unban_id:
            user=User.objects.get(username=unban_id)
            if user.is_banned:
                user.is_banned=False
                user.save()
        return redirect('admin-dash')

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class=LoginSerializer
    
    def post(self, request):
        login_serializer=self.serializer_class(data=request.data)
        if login_serializer.is_valid(raise_exception=True):
            login(request, login_serializer.validated_data.get('user'))
            print(request.user.is_banned)
            if request.user.is_banned:
                return Response({
                    "Error": "Your Account has been banned, please reachout to admin team"
                    })
            
            if request.user.is_superuser:
                return redirect('admin-dash')
            return redirect('news')
        return Response({
            "Error": "Invalid Credentials",
        })


class SearchView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchSerializer
    
    def get(self, request):
        search_output = self.get_queryset()
        result = SearchSerializer(search_output, many=True)
        return render(request, "apiApp/keyword.html", {'data': result.data})
    
    def get_queryset(self):
        return SearchTable.objects.filter(user=self.request.user)
    

class ExistingNewsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer
    
    def get(self, request, **kwargs):
        keyword=kwargs.get("keyword")
        search_obj=SearchTable.objects.get(keyword=keyword)
        articles = Article.objects.filter(user=request.user, keyword=search_obj)
        serzd_data=self.serializer_class(articles, many=True)
        # ddata=[dict(data) for data in serzd_data.data]
        return render(request, "apiApp/search.html", {"data":serzd_data.data, "keyword":keyword})


class RefreshNews(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class=NewsSerializer
    
    def post(self, request):
        data=request.POST
        
        api_url="https://newsapi.org/v2/everything"
        response=requests.get(api_url, params={'apiKey':API_KEY,"q": data.get('keyword'), "from": data.get('from_date')}).json()
        print(response)
        articles=response.get('articles')
        search_obj=SearchTable.objects.get_or_none(user=request.user, keyword=data['keyword'])
        if len(articles):
            search_obj.created_date=datetime.now()
            search_obj.latest_article_date=parse_datetime(articles[0].get("publishedAt"))
            search_obj.save()
                
            instances=[]
            
            for article in articles:
                source=article.pop("source")
                publishedAt=article.pop("publishedAt")
                instances.append(
                    Article(
                        keyword=search_obj,
                        user=request.user,
                        source_id=source.get('id'),
                        source_name=source.get('name'),
                        publishedAt=parse_datetime(publishedAt),
                        **article
                    )
                )
            Article.objects.bulk_create(instances)
        return redirect('existing-view', keyword=data.get('keyword'))


class NewsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class=NewsSerializer
    
    def post(self, request):
        keyword=request.POST.get('keyword')
        source_category=request.POST.get('source_category')
        from_date=request.POST.get('from_date')
        language=request.POST.get('language')
        
        search_obj=SearchTable.objects.get_or_none(user=request.user, keyword=keyword)
        if not search_obj:
            search_obj=SearchTable(
                user=request.user,
                keyword=keyword
            )
        elif datetime.now(pytz.UTC) - timedelta(minutes=15) < search_obj.created_date:
                existing_articles=Article.objects.filter(keyword=search_obj, user=request.user).order_by("-publishedAt")
                serzd_data=ArticleSerializer(existing_articles, many=True)
                return render(request, "apiApp/search.html", {"data":serzd_data.data, "keyword":keyword})
        
        api_url="https://newsapi.org/v2/everything"
        params={
            'q':keyword,
            'apiKey':API_KEY,
            'pageSize':15,
            'page':1
        }
        if source_category:
            api_url="https://newsapi.org/v2/top-headlines"
            params.update({'category':source_category})
        
        if from_date and not source_category:
            from_date=datetime.strptime(from_date,"%Y-%m-%d")
            params.update({'from':from_date})
        
        if language:
            params.update({'language':language})
        
        news_response=requests.get(api_url, params=params).json()
        if news_response.get('status')=="ok":
            articles=news_response.get('articles')
            print(len(articles))
            if len(articles):
                search_obj.created_date=datetime.now()
                search_obj.latest_article_date=parse_datetime(articles[0].get("publishedAt"))
                search_obj.save()
                    
                instances=[]
                for article in articles:
                    source=article.pop("source")
                    publishedAt=article.pop("publishedAt")
                    instances.append(
                        Article(
                            keyword=search_obj,
                            user=request.user,
                            source_id=source.get('id'),
                            source_name=source.get('name'),
                            publishedAt=parse_datetime(publishedAt),
                            **article
                        )
                    )
                Article.objects.bulk_create(instances)
            
                
        else:
            return Response({
                "Error":"Invalid response received from the API."
            })
        
        # return Response(news_response)
        return render(request, "apiApp/search.html", {"data":news_response.get('articles'), "keyword":keyword})
    def get(self, request):
        print("HELLOOOO")
        search_form=SearchForm()
        return render(request, "apiApp/news.html", {'form': search_form})

class UserView(viewsets.ModelViewSet):
    serializer_class=UserSerializer
    # permission_classes=[IsAuthenticated]
    queryset=User.objects.all()
    

        