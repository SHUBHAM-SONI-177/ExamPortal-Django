
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from student.models import question , questionPaper
from .forms import questionForm
from .forms import questionHead
from .forms import studyMaterialForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import login
from .models import faculty
from student.models import liveQuestionPaper
from passlib.hash import pbkdf2_sha256
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
import re

def index(request):
    if request.session.get('slogin',False):
        messages.error(request,"you are already login as student")
        return HttpResponseRedirect('/student/studentpage')
    if request.session.get('flogin',False):
        return HttpResponseRedirect('/faculty/facultypage')
    params={}
    return HttpResponseRedirect('/faculty/facultylogin')

def inputQuestion(request):
    params={}
    if request.session.get('flogin',False):
        if request.method == "POST":
            discount = question(paperID = questionPaper.objects.get(paperID=request.session['questionPaper']))
            form=questionForm(request.POST,request.FILES,instance=discount)
            if form.is_valid():
                form.save()
                if 'addmore' not in request.POST:
                    messages.success(request,'Succesfully Uploaded')
                    return HttpResponseRedirect('facultypage')
            else:
                messages.error(request,"Invalid Inputs")
            return HttpResponseRedirect('questionInput')
        else:
            form=questionForm()
            params['form']=form
            return render(request,'faculty/questionInput.html',params)
    else:
        messages.error(request, 'you have to login to upload queston paper')
        return HttpResponseRedirect('facultylogin',params)


def signup(request):
    params={}
    if not request.session.get('loggedin',False) :
        return render(request,'faculty/signup.html',params)
    else:
        messages.error(request, 'you are already signed in')
        return HttpResponseRedirect('/faculty',params)


def handlelogin(request):
    params={}
    temail=request.POST.get('email')
    tpassword=request.POST.get('password')
    try:
        details=faculty.objects.get(email=temail)
    except:
        messages.error(request, 'wrong credentials')
        return HttpResponseRedirect('facultylogin',params)
    if pbkdf2_sha256.verify(tpassword,details.password):
        if not details.isActive:
             messages.error(request, 'please verify your email by clicking the link you have recieved via email')
             return HttpResponseRedirect('facultylogin',params)
        request.session['loggedin']=True
        request.session['flogin']=True
        request.session['loguser']=temail
        messages.success(request, 'You are logged in succesfully')
        return HttpResponseRedirect('facultypage',params)
    else:
        messages.error(request, 'wrong credentials')
        return HttpResponseRedirect('facultylogin',params)

def facultylogin(request):
    params={}
    if request.session.get('loggedin',False):
        return HttpResponseRedirect('facultypage',params)
    return render(request,'faculty/login.html',params)

def validPass(mypass):
    sPass=len(mypass)>6 and len(mypass)<20 and re.search("[a-z]",mypass) and re.search("[0-9]",mypass) and re.search("[A-Z]",mypass) and re.search("[$#@]",mypass)
    return sPass

def login2(request):
    params={}
    tname=request.POST.get('name','none')
    temail=request.POST.get('email','none')
    tdob=request.POST.get('dob','none')
    taddress=request.POST.get('address','none')
    tpassword=request.POST.get('password','none')
    trepeat_password=request.POST.get('repeat_password','none')
    tprofilepic=request.FILES.get('profilePic','none')
    if not validPass(tpassword):
        messages.error(request,"Passwords must be  greater than 6 charater and less than 20 characters \n must contain at least one lowercase letter, one uppercase letter, one numeric digit, and one special character, but cannot contain whitespace")
        return HttpResponseRedirect('signup',params)
    
    test=faculty.objects.filter(email=temail)
    if len(test)!=0:
        messages.error(request, 'User already exist with this email')
        return HttpResponseRedirect('signup',params)
        
   
    if trepeat_password==tpassword:
        enc_string=pbkdf2_sha256.encrypt(tpassword,rounds=12000,salt_size=32)
        tstudent=faculty(name=tname,email=temail,dob=tdob,address=taddress,password=enc_string,profilePic=tprofilepic)
        tstudent.save()
        current_site = get_current_site(request)
        mail_subject = 'Activate your  account.'
        message = render_to_string('faculty/acc_active_email.html', {
                'user':tstudent,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(temail)),
                'token':account_activation_token.make_token(tstudent),
            })
        to_email = temail
        email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
        email.send()
        messages.success(request,'Please confirm your email address to complete the registration')
        return HttpResponseRedirect('facultylogin',params)
    else:
        messages.error(request, 'passowrd did not match')
        return HttpResponseRedirect('signup',params)
    

def facultylogout(request):
    params={}
    request.session['flogin']=False
    request.session['loggedin']=False
    request.session['loguser']='None'
    return HttpResponseRedirect('/',params)

def activate(request, uidb64, token):
    tpflag=True
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        tstudent = faculty.objects.get(email=uid)
    except:
        tpflag=False
    if tpflag and account_activation_token.check_token(tstudent, token):
        tstudent.isActive = True
        tstudent.save()
        return HttpResponseRedirect('/faculty/facultylogin')
    else:
        return HttpResponse('Activation link is invalid!')


def forgotPassword(request):
        return render(request,'faculty/forgotPassword.html')
def handleForgotPassword(request):
    if request.method=="POST":
        tempmail=request.POST.get('email')
        tstudent=faculty.objects.get(email=tempmail)
        tstudent.isActive=False
        tstudent.save()
        current_site = get_current_site(request)
        mail_subject = 'Change Your Password'
        message = render_to_string('faculty/change_pass_email.html', {
                'user':tstudent,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(tempmail)),
                'token':account_activation_token.make_token(tstudent),
            })
        to_email = tempmail
        email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
        email.send()
        messages.success(request,'Please check your email to change the Password')
        return HttpResponseRedirect('facultylogin')
    else:
        return HttpResponse("invalid request")
def facultyChangePassword(request,uidb64,token):
    tpflag=True
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        tstudent = faculty.objects.get(email=uid)
    except:
        tpflag=False
    if tpflag and account_activation_token.check_token(tstudent, token):
        tstudent.isActive=True
        tstudent.save()
        request.session['uid']=uidb64
        return render(request,'faculty/handleChangePassword.html')
    else:
        return HttpResponse('Activation link is invalid!')
def handleChangePassword(request):
    if request.method=='POST':
        tpflag=True
        try:
            uid = force_text(urlsafe_base64_decode(request.session.get('uid','None')))
            tstudent = faculty.objects.get(email=uid)
            del request.session['uid']
        except:
            return HttpResponse("invalid url")
            tpflag=False
        newp=request.POST.get('newP')
        cnewP=request.POST.get('cnewP')
        
        if tpflag and cnewP and newp==cnewP:
            enc_string=pbkdf2_sha256.encrypt(newp,rounds=12000,salt_size=32)
            updated=faculty.objects.filter(email=uid).update(password=enc_string)
            tstudent.password=enc_string
            tstudent.save()
            messages.success(request,"password changed ")
            return HttpResponseRedirect('facultylogin')
        else:
            messages.error(request,"password is not valid")
            return HttpResponseRedirect('facultylogin')
    else:
        return HttpResponse("invalid request")

def viewProfile(request):
    params={}
    if request.session.get('flogin',False):
        profile= faculty.objects.get(email=request.session.get('loguser','None'))
        params['profile']=profile
        return render(request,"faculty/profile.html",params)
    else:
        messages.error(request, 'first you should login to view your profile')
        return HttpResponseRedirect('facultylogin',params)


def handleUpdateProfilePic(request):
    params={}
    if request.method=='POST':
        if request.session.get('flogin',False):
            tprofilepic=request.FILES.get("profilePic",None)
            profile= faculty.objects.get(email=request.session.get('loguser','None'))
            profile.profilePic=tprofilepic
            profile.save()
            return HttpResponseRedirect('viewProfile',params)
        else:
            messages.error(request,"please login to update profile")
            return HttpResponseRedirect('facultylogin',params)

def handleSetQuizTime(request):
    params={}
    if request.session.get('flogin',False):
        paperID1=request.POST.get("paperID")
        ashu_time=request.POST.get("ashu_time")
        try:
            obj = questionPaper.objects.get(paperID=paperID1)
            obj.duration = ashu_time
            obj.save()
            messages.success(request,"paper time updated")
            return HttpResponseRedirect('facultypage',params)
        except:
            messages.error(request,"paperTime updation failed")
            return HttpResponseRedirect('facultypage',params)
    else:
        messages.error(request,"please login to set Quiz Time")
        return HttpResponseRedirect('facultylogin',params)
        
def handleSetLiveExamPaper(request):
    params={}
    if request.session.get('flogin',False):
        paperID1=request.POST.get("paperID")
        ashu_time=request.POST.get("ashu_time")
        ashu_date=request.POST.get("ashu_date")
        try:
            obj=liveQuestionPaper.objects.filter(paperID=paperID1)
            if len(obj)==0:
                ahsu_temp=liveQuestionPaper(paperID=questionPaper.objects.get(paperID=paperID1),quizTime=ashu_time,paperDate=ashu_date)
                ahsu_temp.save()
            else:
                obj=liveQuestionPaper.objects.get(paperID=questionPaper.objects.get(paperID=paperID1))
                obj.quizTime=ashu_time
                obj.paperDate=ashu_date
                obj.save()
        except:
            messages.error(request,"live paper settting failed")
            return HttpResponseRedirect('facultypage',params)
        messages.success(request,"live Question Paper Added")
        return HttpResponseRedirect('facultypage',params)
    else:
        messages.error(request,"please login to set Live Question Paperr")
        return HttpResponseRedirect('facultylogin',params)
    

def facultypage(request):
    params={}
    if request.session.get('flogin',False):
        profile= faculty.objects.get(email=request.session.get('loguser','None'))
        params['profile']=profile
        if request.method == "POST":
            if 'form1submit' in request.POST:
                form1=questionHead(request.POST,request.FILES)
                if form1.is_valid():
                    paperID1=form1.cleaned_data['paperID']
                    request.session['questionPaper']=paperID1
                    form1.save()
                else:
                    request.session['questionPaper']=request.POST.get('paperID')
                return HttpResponseRedirect('questionInput')

            if 'studymaterialsubmit' in request.POST:
                form=studyMaterialForm(request.POST or None ,request.FILES or None)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Uploaded Succesfully')
                    return HttpResponseRedirect('facultypage')
        else:
            form1=questionHead()
            params['form1']=form1
            form=studyMaterialForm()
            params['form']=form

        paperID=questionPaper.objects.values_list('paperID',flat=True)
        params['paperID']=paperID
        return render(request,"faculty/facultypage.html",params)
    else:
        messages.error(request, 'first you should login')
        return HttpResponseRedirect('facultylogin',params)

def seeQuestionPaper(request):
    params={}
    if request.method=="POST" :
        if request.session.get('flogin',False):
            value=request.POST.get('paperID')
            q=question.objects.filter(paperID=value)
            params['q']=q
            return render(request,"faculty/seeQuestionPaper.html",params)
        else:
            messages.error(request, ' please log in In roder to attempt quiz')
            return HttpResponseRedirect('facultylogin',params)
    else:
        messages.error(request, 'first you should login then only you can see the questions')
        return HttpResponseRedirect('facultylogin',params)


def numberOfQuestion(request):
    if request.session.get('flogin',False):
        return render(request,'faculty/numberOfQuestion.html')


def handleNumberOfQuestion(request):
    if request.method=="POST":
        noq1=request.POST.get('noq')
        try:
            noq2=int(noq1)
            request.session['noq']=noq2
            if noq2>=0:
                return render(request,'faculty/newInputQuestion.html',{"range":range(noq2)})
            else:
                return HttpResponse("Invalid number of question")
        except:
            return HttpResponse("Invalid Input")
    else:
        return HttpResponse("Invalid Request")

def saveQuetion(request):
    if request.method=="POST":
        noq=request.session.get('noq')
        paperID=request.POST.get('paperID','none')
        paperTag=request.POST.get('paperTag','none')
        if paperID=='none':
            return HttpResponse('invalid paper ID')
        try:
            tquestionpaper=questionPaper.objects.get(paperID=paperID)
            tquestionpaper.questionTag=paperTag
            tquestionpaper.save()
        except:
            tquestionpaper=questionPaper(paperID=paperID,questionTag=paperTag)
            tquestionpaper.save()
        tquestionpaper=questionPaper.objects.get(paperID=paperID)
        wrong_indexes = []
        ind = 1
        for i in range(noq):
            qtext="qText"+str(i)
            qImage="qImage"+str(i)
            A="A"+str(i)
            B="B"+str(i)
            C="C"+str(i)
            D="D"+str(i)
            R="R"+str(i)
            M="M"+str(i)
            qtextVal=request.POST.get(qtext,'none')
            qimageVal=request.FILES.get(qImage,'none')
            AVal=request.POST.get(A,'none')
            BVal=request.POST.get(B,'none')
            CVal=request.POST.get(C,'none')
            DVal=request.POST.get(D,'none')
            RVal=request.POST.get(R,'none')
            MVal=request.POST.get(M,'none')
            if(AVal!='none' and BVal!='none' and CVal!='none' and DVal!='none' and RVal!='none' and (RVal in ['A','B','C','D']) and qtextVal!='none'):
                tquestion=question(paperID=tquestionpaper,questionText=qtextVal,option1=AVal,option2=BVal,option3=CVal,option4=DVal,rightOption=RVal)
                try:
                    tquestion.questionMarks=int(MVal)
                    tquestion.save()
                    if qimageVal!='none':
                        tquestion.questionImage=qimageVal
                        tquestion.save()
                except:
                    wrong_indexes.append(ind)
            else:
                wrong_indexes.append(ind)
            ind += 1
        if len(wrong_indexes)>0:
            msg_wrong = "invalid inputs for questions "
            for i in wrong_indexes:
                msg_wrong += str(i)+" "
            messages.error(request,msg_wrong)
        else:
            messages.success(request,'Uploaded Successfully')
        return HttpResponseRedirect("facultypage")
    else:
        return HttpResponse("invalid request")



