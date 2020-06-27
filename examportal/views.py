from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
def index(request):
    if request.session.get('slogin',False):
        return HttpResponseRedirect('/student/studentpage')
    if request.session.get('flogin',False):
        return HttpResponseRedirect('/faculty/facultypage')
    return render(request,'index.html')