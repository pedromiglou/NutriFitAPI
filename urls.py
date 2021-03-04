"""Projeto1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from NutriFit import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    path('', admin.site.urls),
    path('ws/register', views.register_user),
    path('ws/statistics', views.daily_statistics),
    path('ws/login/', obtain_jwt_token, name='token_obtain_pair'),
    path('ws/refresh/', refresh_jwt_token, name='token_refresh'),
    path('ws/updateCI/', views.update_ci),
    path('ws/updateBMI/', views.update_bmi),
    path('ws/getmeal', views.getMeal),
    path('ws/getfoodlist', views.getFoodList),
    path('ws/addfoodtomeal', views.insertComposta),
    path('ws/updatefoodtomeal', views.updateComposta),
    path('ws/deletefoodfrommeal/<int:id>', views.deleteComposta),
    path('ws/getfood', views.getFood),
    path('ws/getuser', views.getUser),
    path('ws/setuser', views.setUser),
    path('ws/setpassword', views.setPassword),
    path('ws/getprofile', views.getProfile),
    path('ws/updateprofile', views.updateProfile),
    path('ws/addfood', views.addFood),
    path('ws/updatefood', views.updateFood),
    path('ws/deletefood/<int:id>', views.deleteFood),
    path('ws/getusers', views.getUsers),
    path('ws/upgradeuser', views.updateUserUp),
    path('ws/downgradeuser', views.updateUserDown),
    path('ws/getcategories', views.getCategories),
    path('ws/postcategory', views.postCategory),
    path('ws/deletecategory/<int:id>', views.deleteCategory),
    path('ws/getpermissions', views.getPermissions)
]
