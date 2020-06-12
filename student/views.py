from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import student
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import login
from .models import question
from .models import performance
from datetime import datetime,timedelta,date
from .models import studyMaterial
from .models import paperTime
from .models import liveQuestionPaper
from .models import liveTestPerformance
from django.db.models import query_utils,query,Q
from passlib.hash import pbkdf2_sha256
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


import re

from .forms import SetPasswordForm


params={'slogin':False,'flogin':False,'alogin':False,'loggedin':False,'loguser':'None'}
def index(request):
    global params
    return render(request,'student/index.html',params)
def signup(request):
    global params
    if not request.session.get('loggedin',False) :
        return render(request,'student/signup.html',params)
    else:
        return HttpResponseRedirect('/',params)

def handlelogin(request):
     global params
     temail=request.POST.get('email')
     tpassword=request.POST.get('password')
     #user = authenticate(username=temail, password=tpassword)
     try:
         details=student.objects.get(email=temail)
     except:
         messages.error(request, 'wrong credentials')
         return HttpResponseRedirect('studentlogin',params)
     if  pbkdf2_sha256.verify(tpassword,details.password):
         if not details.isActive:
             messages.error(request, 'please verify your email by clicking the link you have recieved via email')
             return HttpResponseRedirect('studentlogin',params)
         request.session['slogin']=True
         request.session['loguser']=temail
         request.session['loggedin']=True
         params['loggedin']=True
         params['slogin']=True
         params['loguser']=temail
         #login(request,user)
         messages.success(request, 'You are logged in succesfully')
         return HttpResponseRedirect('studentpage',params)
     else:
         messages.error(request, 'wrong credentials')
         return HttpResponseRedirect('studentlogin',params)
def studentlogin(request):
    global params
    if request.session.get('loggedin',False):
        return HttpResponseRedirect('studentpage',params)
    return render(request,'student/login.html',params)
def validPass(mypass):
    sPass=len(mypass)>6 and len(mypass)<20 and re.search("[a-z]",mypass) and re.search("[0-9]",mypass) and re.search("[A-Z]",mypass) and re.search("[$#@]",mypass)
    return sPass
def login2(request):
    tname=request.POST.get('name','none')
    temail=request.POST.get('email','none')
    tdob=request.POST.get('dob','none')
    taddress=request.POST.get('address','none')
    tpassword=request.POST.get('password','none')
    trepeat_password=request.POST.get('repeat_password','none')
    tprofilepic=request.FILES.get('profilePic','none')
    
    test=student.objects.filter(email=temail)
    if not validPass(tpassword):
        messages.error(request,"Passwords must be  greater than 6 charater and less than 20 characters \n and  must contain at least one lowercase letter, one uppercase letter, one numeric digit, and one special character, but cannot contain whitespace")
        return HttpResponseRedirect('signup',params)
    if len(test)!=0:
        messages.error(request, 'User already exist with this email')
        return HttpResponseRedirect('signup',params)
        
   
    if trepeat_password==tpassword:
        enc_string=pbkdf2_sha256.encrypt(tpassword,rounds=12000,salt_size=32)
        tstudent=student(name=tname,email=temail,dob=tdob,address=taddress,password=enc_string,profilePic=tprofilepic,isActive=False)
        tstudent.save()

        current_site = get_current_site(request)
        mail_subject = 'Please verify  your  email.'
        message = render_to_string('student/acc_active_email.html', {
                'user':tstudent,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(temail)),
                'token':account_activation_token.make_token(tstudent),
            })
        print(message)
        print(current_site)
        print(current_site.domain)
        print(urlsafe_base64_encode(force_bytes(temail)))
        to_email = temail
        email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
        email.send()
        #request.session['rguser']=temail
        messages.success(request,'Please confirm your email address to complete the registration')
        return HttpResponseRedirect('studentlogin',params)
        #tuser = User.objects.create_user(username=temail,email=temail,password=tpassword)
        #tuser.save()                             
    else:
        messages.error(request, 'passowrd did not match')
        return HttpResponseRedirect('signup',params)
    
def studentActivate(request, uidb64, token):
    tpflag=True
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        #tstudent = student.objects.get(email=request.session.get('rguser','None'))
        tstudent = student.objects.get(email=uid)
        #del request.session['rguser']
    except:
        tpflag=False
    if tpflag and account_activation_token.check_token(tstudent, token):
        tstudent.isActive = True
        tstudent.save()
        return HttpResponseRedirect('/student/studentlogin')
    else:
        return HttpResponse('Activation link is invalid!')
def studentlogout(request):
    global params
    request.session['slogin']=False
    request.session['loguser']='None'
    request.session['loggedin']=False
    params['slogin']=False
    params['loggedin']=False
    params['loguser']='None'
    return HttpResponseRedirect('/',params)
def forgotPassword(request):
    if not request.session.get('slogin',False):
         return render(request,'student/forgotPassword.html')
def handleForgotPassword(request):
    print("lest do it")
    if request.method=="POST":
        print("i am here")
        tempmail=request.POST.get('email')
        
        tstudent=student.objects.get(email=tempmail)
        tstudent.isActive=False
        tstudent.save()
        current_site = get_current_site(request)
        mail_subject = 'Change Your Password'
        message = render_to_string('student/change_pass_email.html', {
                'user':tstudent,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(tempmail)),
                'token':account_activation_token.make_token(tstudent),
            })
        print(message)
        print(current_site)
        print(current_site.domain)
        print(urlsafe_base64_encode(force_bytes(tempmail)))
        to_email = tempmail
        email = EmailMessage(
                        mail_subject, message,to=[to_email]
            )
        email.send()
        messages.success(request,'Please check your email to change the Password')
        return HttpResponseRedirect('studentlogin')
    else:
        return HttpResponse("invalid request")
def changePassword(request,uidb64,token):
    tpflag=True
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        tstudent = student.objects.get(email=uid)
    except:
        tpflag=False
    if tpflag and account_activation_token.check_token(tstudent, token):
        tstudent.isActive=True
        tstudent.save()
        request.session['uid']=uidb64
        return render(request,'student/handleChangePassword.html')
    else:
        return HttpResponse('Activation link is invalid!')

def handleChangePassword(request):
    if request.method=='POST':
        tpflag=True
        try:
            uid = force_text(urlsafe_base64_decode(request.session.get('uid','None')))
            tstudent = student.objects.get(email=uid)
            del request.session['uid']
        except:
            return HttpResponse("invalid url")
            tpflag=False
        newp=request.POST.get('newP')
        cnewP=request.POST.get('cnewP')
        
        if tpflag and cnewP and newp==cnewP:
            print(newp)
            print(tstudent.password)
            enc_string=pbkdf2_sha256.encrypt(newp,rounds=12000,salt_size=32)
            updated=student.objects.filter(email=uid).update(password=enc_string)
            tstudent.password=enc_string
            tstudent.save()
            print(pbkdf2_sha256.verify(cnewP,tstudent.password))
            print(updated)
            print(tstudent.password)
            messages.success(request,"password changed ")
            return HttpResponseRedirect('studentlogin')
        else:
            messages.error(request,"password is not valid")
            return HttpResponseRedirect('studentlogin')
    else:
        return HttpResponse("invalid request")




def attemptQuiz(request):
    global params
    if request.method=="POST" :
        if request.session.get('slogin',False):
            value=request.POST.get('paperID1')
            q=question.objects.filter(paperID=value)
            print("it is me")
            try:
                print("itsm me1")
                q1=liveQuestionPaper.objects.get(paperID=value)
                
                currentTime=datetime.now()
                qtime=q1.quizTime
                qdate=q1.paperDate
                print(qtime)
                newdateTime=datetime.combine(qdate,qtime)
                newdateTime=newdateTime+timedelta(hours=5)
                if currentTime<newdateTime:
                    tempmessage="you can attempt this paper after"
                    tempmessage=tempmessage+newdateTime.strftime("%b %d %Y %H:%M")
                    messages.error(request,tempmessage)
                    return HttpResponseRedirect("studentpage",params)
            except:
                pass
            params['q']=q
            params['paperID']=value
            request.session['paperID']=value
            try:
                obj=paperTime.objects.get(paperID=value)
                params['ashu_time']=obj.quizTime
            except:
                params['ashu_time']=60

            
            return render(request,"student/attemptQuiz.html",params)
        else:
            messages.error(request, ' please log in In roder to attempt quiz')
            return HttpResponseRedirect('studentlogin',params)
    else:
        messages.error(request, 'first you should choose paper then only you can access the the quiz')
        return HttpResponseRedirect('studentpage',params)


def handleAttemptQuiz(request):
    global params
    if request.method=='POST':
        q=question.objects.filter(paperID=request.session['paperID']).values()
        total=0
        right=0
        r1=0
        t1=0
        for obj in q:
            name=obj['questionText']
            value=request.POST.get(name)
            print(name)
            t1=t1+1
            total=total+obj['questionMarks']
            if value==obj['rightOption']:
                right=right+obj['questionMarks']
                r1=r1+1
                print("you are goddamn right")
            else:
                print("you are wrong")
        percentage=right/total
        percentage=percentage*100
        try:
            print("before1")
            newp=performance.objects.get(paperID=request.session['paperID'],studentID=request.session['loguser'])
            print("brfor2")
            if(newp.percentageMarks<percentage):
                newp.percentageMarks=percentage
                newp.time=datetime.now()
                newp.save()
        except:
            print("brfor3")
            newp=performance(studentID=request.session['loguser'],paperID=request.session['paperID'],time=datetime.now(),percentageMarks=percentage)
            newp.save()
        params['marks']=percentage
        params['rightQuestion']=r1
        params['totalQuestion']=t1
        del request.session['paperID']
        return render(request,"student/result.html",params)
    else:
        return HttpResponse("invalid access")

def viewProfile(request):
    if request.session.get('slogin',False):
        profile= student.objects.get(email=request.session['loguser'])
        studentPerformance=performance.objects.filter(studentID=request.session['loguser'])
        params['profile']=profile
        params['stp']=studentPerformance
        return render(request,"student/profile.html",params)
    else:
        messages.error(request, 'first you should login to view your profile')
        return HttpResponseRedirect('studentlogin',params)

def handleUpdateProfilePic(request):
    if request.method=='POST':
        if request.session.get('slogin',False):
            tprofilepic=request.FILES.get("profilePic",None)
            profile= student.objects.get(email=request.session['loguser'])
            profile.profilePic=tprofilepic
            profile.save()
            return HttpResponseRedirect('viewProfile',params)
        else:
            messages.error(request,"please login to update profile")
            return HttpResponseRedirect('studentlogin',params)
    
def liveAttemptQuiz(request):
    global params
    if request.method=="POST" :
        if request.session.get('slogin',False):
            value=request.POST.get('paperID2')
            q=question.objects.filter(paperID=value)
            print("itsm me")
            try:
                print("itsm me1")
                q1=liveQuestionPaper.objects.get(paperID=value)
                currentTime=datetime.now()
                qtime=q1.quizTime
                qdate=q1.paperDate
                newdateTime=datetime.combine(qdate,qtime)
                obj21=paperTime.objects.get(paperID=value)
                enddatetime=newdateTime+timedelta(minutes=obj21.quizTime)
                if currentTime<newdateTime or currentTime>enddatetime:
                    tempmessage="you can attempt this paper after"
                    tempmessage=tempmessage+newdateTime.strftime("%b %d %Y %H:%M")
                    print(tempmessage)
                    messages.error(request,tempmessage)
                    return HttpResponseRedirect("studentpage",params)
            except:
                pass
            params['q']=q
            params['ashu_paperID']=value
            params['paperID']=value
            request.session['paperID']=value
            try:
                obj=paperTime.objects.get(paperID=value)
                params['ashu_time']=obj.quizTime
            except:
                params['ashu_time']=60
            return render(request,"student/liveAttemptQuiz.html",params)
        else:
            messages.error(request, ' please log in In roder to attempt quiz')
            return HttpResponseRedirect('studentlogin',params)
    else:
        messages.error(request, 'first you should choose paper then only you can access the the quiz')
        return HttpResponseRedirect('studentpage',params)

def handleLiveAttemptQuiz(request):
    global params
    if request.method=='POST':
        q=question.objects.filter(paperID=request.session['paperID']).values()
        total=0
        right=0
        r1=0
        t1=0
        for obj in q:
            name=obj['questionText']
            value=request.POST.get(name)
            print(name)
            t1=t1+1
            total=total+obj['questionMarks']
            if value==obj['rightOption']:
                right=right+obj['questionMarks']
                r1=r1+1
                print("you are goddamn right")
            else:
                print("you are wrong")
        percentage=right/total
        percentage=percentage*100
        newp=performance(studentID=request.session['loguser'],paperID=request.session['paperID'],time=datetime.now(),percentageMarks=percentage)
        newp.save()
        params['marks']=percentage
        params['rightQuestion']=r1
        params['totalQuestion']=t1
        tempobj=liveTestPerformance.objects.filter(studentID=request.session['loguser'])
        if len(tempobj)==0:
            newPerformance=liveTestPerformance(studentID=request.session['loguser'],paperID=request.session['paperID'],studentMarks=percentage)
            newPerformance.save()
            print(newPerformance)
            del request.session['paperID']
        else:
            return HttpResponse("invalid access")    
        return render(request,"student/result.html",params)
    else:
        return HttpResponse("invalid access")

def handleLeaderBoard(request):
    global params
    if request.method=="POST" :
        if request.session.get('slogin',False):
            value=request.POST.get('paperID')
            leaders=liveTestPerformance.objects.filter(paperID=value)
            leaders=leaders.values()
            if len(leaders)==0:
                return HttpResponse("No data to show")
            sorted(leaders,key=lambda i:i['studentMarks'],reverse=True)
            params['leaders']=leaders
            return render(request,"student/handleLeaderBoard.html",params)
        else:
            messages.error(request, ' please login in roder to attempt quiz')
            return HttpResponseRedirect('studentlogin',params)
    else:
        messages.error(request, 'first you should choose paper then only you can access the the leaderBoard')
        return HttpResponseRedirect('studentpage',params)

def studentpage(request):
    if request.session.get('slogin',False):
        books=studyMaterial.objects.all()
        params['books']=books
        profile= student.objects.get(email=request.session['loguser'])
        params['profile']=profile
        paperID=question.objects.values_list('paperID',flat=True).distinct()
        params['paperID']=paperID
        cdate=date.today()
        paperID1=liveQuestionPaper.objects.all()
        paperID2=[]
        fdate=[]
        for obj in paperID1:
            newtime=datetime.combine(obj.paperDate,obj.quizTime)
            obj21=paperTime.objects.get(paperID=obj.paperID)
            enddatetime=newtime+timedelta(minutes=obj21.quizTime)
            if newtime>datetime.now() or (datetime.now()>newtime and datetime.now()<enddatetime):
                paperID2.append(obj)       
        params['paperID2']=paperID2
        return render(request,"student/studentpage.html",params)
    else:
        messages.error(request, 'first you should login')
        return HttpResponseRedirect('studentlogin',params)