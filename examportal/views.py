from django.shortcuts import render
from django.http import HttpResponse
from student.views import params
def index(request):
    return render(request,'index.html',params)