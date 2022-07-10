"""firstproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from board import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name="home"),
    path('main/', views.main),
    path('main_new/', views.main_new),
    path('crawling_today_hk/', views.crawling_today_hk, name="hk"),
    path('crawling_today_ja/', views.crawling_today_ja, name="ja"),
    path('crawling_today_mk/', views.crawling_today_mk, name="mk"),
    path('test/', views.test),
    path('board/', include('board.urls'))
]
