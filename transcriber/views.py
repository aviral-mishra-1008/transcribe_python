from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import os
import whisper
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import dotenv
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


dotenv.load_dotenv()
#load model
model = whisper.load_model("base")

def home(request):
    return render(request,"home.html")

@csrf_exempt
def save_audio(request):
    if request.method == 'POST':
        mp3_data = request.FILES.get('audioRecording')
        temp_folder = 'temp/'  
        mp3_path = os.path.join(temp_folder, 'file82.wav')

        with open(mp3_path, 'wb') as mp3_file:
            for chunk in mp3_data.chunks():
                mp3_file.write(chunk)

        result = model.transcribe("temp/file82.wav")
        os.remove("temp/file82.wav")
        
        with open('counts.pkl','rb') as f:
            count = pickle.load(f)

        rootPath = 'temp/transcriptions/'+str(count)+'.txt'

        with open(rootPath,'w') as f:
            f.write(result['text'])
        
        count+=1

        with open('counts.pkl','wb') as f:
            pickle.dump(count,f)
        
        emailid = os.environ.get("USER-NAME")
        password = os.environ.get("PASS")
        email = request.user.username

        file_path = rootPath

        with open(file_path, "rb") as file:
            file_content = file.read()

        msg = MIMEMultipart()
        msg["From"] = emailid
        msg["To"] = email
        msg["Subject"] = "Success!!"
        msg.attach(MIMEText("We Have Transcribed The File For You!!", "plain"))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(file_content)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(emailid, password)
            server.sendmail(emailid, email, msg.as_string())
        
        os.remove(rootPath)

    return render(request,"success.html")
    
def signUp(request):
    if request.method=="POST":
            email = request.POST.get('email')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')

            if pass1!=pass2:
                    messages.error(request, "Passwords Didn't Match, Try Again!")
                    return redirect("/")
            
            try:
                actor = User.objects._create_user(email,email,pass1)
                    
            except:
                messages.error(request,"You have already registered!! Sign-In Instead")
                return redirect("/profLogin")
    
            actor.first_name = fname
            actor.last_name = lname
            actor.save()
            messages.success(request,"Please Login")
            return redirect("/")
    return render(request,"signups.html")
    

def signIn(request):
    if request.method =="POST":
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        try:
            obj = User.objects.filter(username=username)
            obj = obj[0]
        except:
            messages.error(request,"You Are Not Registered")
            return redirect('/')
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request,user)
            messages.success(request,"Logged-In!")
            return redirect("/record/")
        else:
            messages.error(request,"Incorrect Credentials!!")
            return redirect("")
    return render(request,"logins.html")

def signOut(request):
    x = logout(request)
    messages.success(request,"Successfully Logged Out!")
    return redirect("/")

def record(request):
    return render(request,"record.html")


def contact(request):
    return render(request,'contact.html')