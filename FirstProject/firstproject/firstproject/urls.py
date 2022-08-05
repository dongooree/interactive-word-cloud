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
    path('monthly/', views.monthly),
    path('main_new/', views.main_new),
    path('fetch_all/', views.fetch_all, name='fetch_all'),
    path('fetch_cs/', views.fetch_cs, name="fetch_cs"), 
    path('wordcloud_cs/', views.wordcloud_cs, name="wordcloud_cs"), 
    path('fetch_ja/', views.fetch_ja, name="fetch_ja"),
    path('wordcloud_ja/', views.wordcloud_ja, name="wordcloud_ja"), 
    path('fetch_hk/', views.fetch_hk, name="fetch_hk"),
    path('wordcloud_hk/', views.wordcloud_hk, name="wordcloud_hk"),
    path('crawling_today_mk/', views.crawling_today_mk, name="mk"),
    # path('crawling_today_kh/', views.crawling_today_kh, name="kh"),
    path('fetch_kh/', views.fetch_kh, name="fetch_kh"),
    path('wordcloud_kh/', views.wordcloud_kh, name="wordcloud_kh"), 
    path('crawling_today_se/', views.crawling_today_se, name="se"),
    path('crawling_today_sg/', views.crawling_today_sg, name="sg"),
    path('test/', views.test),
    path('board/', include('board.urls'))
]
