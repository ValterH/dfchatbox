# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 19:14:01 2018

@author: Jan Jezersek
"""

from django.urls import path
from django.contrib.auth import logout
from . import views

app_name = 'dfchatbox'
urlpatterns = [
        path('',views.index,name='index'),
        path('check_links',views.check_links,name='check_links'),
        path('webhook',views.webhook,name='webhook')
        ]