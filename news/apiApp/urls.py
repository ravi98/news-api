from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'', UserView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('', LoginView.as_view(), name='user-login'),
    path('news/', NewsView.as_view(), name='news'),
    path('refresh-news/', RefreshNews.as_view(), name='refresh-news'),
    path('searches/', SearchView.as_view(), name="user-search"),
    path('existingview/<str:keyword>/', ExistingNewsView.as_view(), name="existing-view"),
    path('logout/', LogoutView.as_view(), name="user-logout"),
    path('admin-dash/', AdminDash.as_view(), name='admin-dash'),
    path('user/', include(router.urls)),
]
