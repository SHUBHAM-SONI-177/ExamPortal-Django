"""examportal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from . import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
     path("", views.index, name="StudentHome"),
     path("signup",views.signup,name="signup"),
     path("login2",views.login2,name="login2"),
     path("studentlogin",views.studentlogin,name="login"),
     path("handlelogin",views.handlelogin,name="handlelogin"),
     path("studentlogout",views.studentlogout,name="studentlogout"),
     path("attemptQuiz",views.attemptQuiz,name="attemptQuiz"),
     path("handleAttemptQuiz",views.handleAttemptQuiz,name="handleAttemptQuiz"),
     path("viewProfile",views.viewProfile,name="viewProfile"),
     path("handleUpdateProfilePic",views.handleUpdateProfilePic,name="handleUpdateProfilePic"),
     path("liveAttemptQuiz",views.liveAttemptQuiz,name="liveAttemptQuiz"),
     path("handleLiveAttemptQuiz",views.handleLiveAttemptQuiz,name="handleLiveAttemptQuiz"),
     path("handleLeaderBoard",views.handleLeaderBoard,name="handleLeaderBoard"),
     path("studentpage",views.studentpage,name="StudentPage"),
     path("forgotPassword",views.forgotPassword,name="forgotPassword"),
     path("handleForgotPassword",views.handleForgotPassword,name="handleForgotPassword"),
     path("handleChangePassword",views.handleChangePassword,name="handleChangePassword"),
     url(r'^studentActivate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        views.studentActivate, name='studentActivate'),
      url(r'^changePassword/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        views.changePassword, name='changePassword'),
]


