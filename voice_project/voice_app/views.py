from django.shortcuts import render, redirect
# from . import forms
from .models import Details
from .models import Compose
import imaplib,email
from gtts import gTTS
import os
from playsound import playsound
from django.http import HttpResponse
import speech_recognition as sr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from django.http import JsonResponse
import re
import pygame
import time
# Predefined dictionary with regular password as key and app password as value
password_dict = {
    "abcd@1234": "nqqktfgrxywdiabh",
    "a1b2c3@4":"jaqdiwjjhibopqf"
}

file = "good"
i = "0"
passwrd = ""
addr = ""
item = ""
subject = ""
body = ""
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
imap_url = 'imap.gmail.com'
conn = imaplib.IMAP4_SSL(imap_url)
attachment_dir = 'C:/Users/text/'

# Function to convert special characters in email address and password
def convert_special_char(text):
    temp = text
    special_chars = ['attherate', 'dot', 'underscore', 'dollar', 'hash', 'star', 'plus', 'minus', 'space', 'dash']
    for character in special_chars:
        while True:
            pos = temp.find(character)
            if pos == -1:
                break
            else:
                if character == 'attherate':
                    temp = temp.replace('attherate', '@')
                elif character == 'dot':
                    temp = temp.replace('dot', '.')
                elif character == 'underscore':
                    temp = temp.replace('underscore', '_')
                elif character == 'dollar':
                    temp = temp.replace('dollar', '$')
                elif character == 'hash':
                    temp = temp.replace('hash', '#')
                elif character == 'star':
                    temp = temp.replace('star', '*')
                elif character == 'plus':
                    temp = temp.replace('plus', '+')
                elif character == 'minus':
                    temp = temp.replace('minus', '-')
                elif character == 'space':
                    temp = temp.replace('space', '')
                elif character == 'dash':
                    temp = temp.replace('dash', '-')
    return temp

# Function to convert text to speech
def texttospeech(text, filename):
    filename = filename + '.mp3'
    flag = True
    while flag:
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            flag = False
        except Exception as e:
            print(f"Error generating speech: {e}")
            print('Trying again')

    # Ensure the file exists before playing
    if os.path.exists(filename):
        print(f"File exists at: {os.path.abspath(filename)}")
        
        # Initialize pygame mixer and play the file
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait until the sound finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Check every 10ms

        print("Audio finished playing")
        
        # No deletion of audio files here
        print(f"The file {filename} is left untouched and not deleted.")
    else:
        print(f"Error: {filename} does not exist.")

# Function to convert speech to text
def speechtotext(duration):
    global i, addr, passwrd
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)

        # Ensure speak.mp3 file is available and accessible
        texttospeech('speak', 'speak')

        # Add a short delay before continuing to allow file access to be released
        time.sleep(1)

        # Listen for the input (speech)
        audio = r.listen(source, phrase_time_limit=duration)

    try:
        response = r.recognize_google(audio)
    except Exception as e:
        print(f"Error during speech recognition: {e}")
        response = 'N'
    
    return response

def remove_non_audio_files():
    # Path to the directory containing the files
    directory = os.getcwd()  # Current working directory

    # Get all files in the directory
    all_files = os.listdir(directory)

    for file in all_files:
        # Remove files that are not mp3 files
        if not file.endswith('.mp3'):
            try:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
                print(f"Deleted non-audio file: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")


# View for login functionality
def login_view(request):
    global i, addr, passwrd 

    if request.method == 'POST':
        # Example of how to use the updated text-to-speech function
        print("Clicked login")
        text1 = "Welcome to our Voice-Based Email. Login with your email account in order to continue. "
        texttospeech(text1, file + i)
        i = str(int(i) + 1)  # Increment to keep the filename unique

        flag = True
        while (flag):
            texttospeech("Enter your Email", file + i)
            i = str(int(i) + 1)  # Increment
            addr = speechtotext(10)

            if addr != 'N':
                addr = addr.strip().lower().replace(' ', '')
                addr = convert_special_char(addr)
                texttospeech(f"You meant {addr}. Say yes please to confirm or no to enter again", file + i)
                i = str(int(i) + 1)
                say = speechtotext(3)

                if say.lower() == 'yes please' or say.lower() == 's please':
                    flag = False
                    break
                else:
                    print(say.lower())
            else:
                texttospeech("Could not understand what you meant. Please try again.", file + i)
                i = str(int(i) + 1)

        # Request email is now set, proceed to password
        flag = True
        while (flag):
            texttospeech("Enter your password", file + i)
            i = str(int(i) + 1)
            passwrd = speechtotext(10)

            if addr != 'N' and passwrd != 'N':
                passwrd = passwrd.strip().lower().replace(' ', '')
                passwrd = convert_special_char(passwrd)
                texttospeech(f"You meant {passwrd}. Say yes please to confirm or no to enter again", file + i)
                i = str(int(i) + 1)
                say = speechtotext(3)

                if say.lower() == 'yes please' or say.lower() == 's please':
                    flag = False
            else:
                texttospeech("Could not understand what you meant. Please try again.", file + i)
                i = str(int(i) + 1)

        # Now proceed to validate the password
        if passwrd in password_dict:
            passwrd = password_dict[passwrd]
            passwrd = passwrd.replace(' ', '')
            print(passwrd)
        # Attempt login with email and app password
        imap_url = 'imap.gmail.com'
        conn = imaplib.IMAP4_SSL(imap_url, 993)
        try:
            print("Attempting login...")
            conn.login(addr, passwrd)
            s.login(addr, passwrd)
            print("Login successful")
            texttospeech("Login successful. You are now redirected to the menu.", file + i)
            i = str(int(i) + 1)
            return JsonResponse({'result': 'success'})
        except Exception as e:
            print(f"Failed login attempt for {addr} with password {passwrd}: {e}")
            texttospeech("Invalid login details. Please try again.", file + i)
            i = str(int(i) + 1)
            return JsonResponse({'result': 'failure'})

    detail = Details()
    detail.email = addr
    detail.password = passwrd
    return render(request, 'login.html', {'detail': detail})



def options_view(request):
    global i, addr, passwrd
    if request.method == 'POST':
        print("Clicked options")
        flag = True
        texttospeech("You are logged into your account. What would you like to do ?", file + i)
        i = i + str(1)
        while(flag):
            texttospeech(".say Compose Inbox Sent Bin Logout . Do you want me to repeat?", file + i)
            i = i + str(1)
            say = speechtotext(3)
            if say.lower()!="yes please":
                flag = False
        texttospeech("Enter your desired action", file + i)
        i = i + str(1)
        act = speechtotext(5)
        act = act.lower()
        if act == 'compose':
            return JsonResponse({'result' : 'compose'})
        elif act == 'inbox':
            return JsonResponse({'result' : 'inbox'})
        elif act == 'send' or act=='sent' or act=='outbox' :
            return JsonResponse({'result' : 'sent'})
        elif act == 'bin' or act == 'trash' or act=='trashbin':
            return JsonResponse({'result' : 'trash'})
        elif act == 'log out':
            addr = ""
            passwrd = ""
            texttospeech("You have been logged out of your account and now will be redirected back to the login page.",file + i)
            i = i + str(1)
            return JsonResponse({'result': 'logout'})
        else:
            texttospeech("Invalid action. Please try again.", file + i)
            i = i + str(1)
            return JsonResponse({'result': 'failure'})
    elif request.method == 'GET':
        return render(request, 'options.html')


def compose_view(request):
    global i, addr, passwrd, s, item, subject, body
    if request.method == 'POST':
        print("clicked compose")
        text1 = "You have reached the page where you can compose and send an email. "
        texttospeech(text1, file + i)
        i = i + str(1)
        flag = True
        flag1 = True
        fromaddr = addr
        toaddr = list()
        while flag1:
            while flag:
                texttospeech("enter receiver's email address:", file + i)
                i = i + str(1)
                to = ""
                to = speechtotext(15)
                if to != 'N':
                    print(to)
                    texttospeech("You meant " + to + " say yes please to confirm or no to enter again", file + i)
                    i = i + str(1)
                    say = speechtotext(5)
                    if say.lower() == 'yes please':
                        toaddr.append(to)
                        flag = False
                else:
                    texttospeech("could not understand what you meant", file + i)
                    i = i + str(1)
            texttospeech("Do you want to enter more recipients ?  Say yes please or no.", file + i)
            i = i + str(1)
            say1 = speechtotext(3)
            if say1.lower() !="yes please":
                print("NOOOO")
                flag1 = False
            flag = True

        newtoaddr = list()
        for item in toaddr:
            item = item.strip()
            item = item.replace(' ', '')
            item = item.lower()
            item = convert_special_char(item)
            newtoaddr.append(item)
            print(item)

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = ",".join(newtoaddr)
        flag = True
        while (flag):
            texttospeech("enter subject", file + i)
            i = i + str(1)
            subject = speechtotext(10)
            if subject == 'N':
                texttospeech("could not understand what you meant", file + i)
                i = i + str(1)
            else:
                flag = False
        msg['Subject'] = subject
        flag = True
        while flag:
            texttospeech("enter body of the mail", file + i)
            i = i + str(1)
            body = speechtotext(20)
            if body == 'N':
                texttospeech("could not understand what you meant", file + i)
                i = i + str(1)
            else:
                flag = False

        msg.attach(MIMEText(body, 'plain'))
        texttospeech("any attachment? say yes please or no", file + i)
        i = i + str(1)
        x = speechtotext(3)
        x = x.lower()
        if x == 'yes please':
            texttospeech("Do you want to record an audio and send as an attachment?", file + i)
            i = i + str(1)
            say = speechtotext(2)
            say = say.lower()
            if say == 'yes please':
                texttospeech("Enter filename.", file + i)
                i = i + str(1)
                filename = speechtotext(5)
                filename = filename.lower()
                filename = filename + '.mp3'
                filename = filename.replace(' ', '')
                print(filename)
                texttospeech("Enter your audio message.", file + i)
                i = i + str(1)
                audio_msg = speechtotext(10)
                flagconf = True
                while flagconf:
                    try:
                        tts = gTTS(text=audio_msg, lang='en', slow=False)
                        tts.save(filename)
                        flagconf = False
                    except:
                        print('Trying again')
                attachment = open(filename, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                msg.attach(p)
            elif say == 'no':
                texttospeech("Enter filename with extension", file + i)
                i = i + str(1)
                filename = speechtotext(5)
                filename = filename.strip()
                filename = filename.replace(' ', '')
                filename = filename.lower()
                filename = convert_special_char(filename)
                
                attachment = open(filename, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                msg.attach(p)
        try:
            print("send re")
            s.login(addr, passwrd)
            s.sendmail(fromaddr, newtoaddr, msg.as_string())
            texttospeech("Your email has been sent successfully. You will now be redirected to the menu page.", file + i)
            i = i + str(1)
        except:
            texttospeech("Sorry, your email failed to send. please try again. You will now be redirected to the the compose page again.", file + i)
            i = i + str(1)
            return JsonResponse({'result': 'failure'})
        s.quit()
        return JsonResponse({'result' : 'success'})
    
    compose  = Compose()
    compose.recipient = item
    compose.subject = subject
    compose.body = body

    return render(request, 'compose.html', {'compose' : compose})
   
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def get_attachment(msg):
    global i
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if bool(filename):
            filepath = os.path.join(attachment_dir, filename)
            with open(filepath, "wb") as f:
                f.write(part.get_payload(decode=True))
                texttospeech("Attachment has been downloaded", file + i)
                i = i + str(1)
                path = 'C:/Users/text/'
                files = os.listdir(path)
                paths = [os.path.join(path, basename) for basename in files]
                file_name = max(paths, key=os.path.getctime)
            with open(file_name, "rb") as f:
                if file_name.find('.jpg') != -1:
                    texttospeech("attachment is an image", file + i)
                    i = i + str(1)
                if file_name.find('.png') != -1:
                    texttospeech("attachment is an image", file + i)
                    i = i + str(1)
                if file_name.find('.mp3') != -1:
                    texttospeech("Playing the downloaded audio file.", file + i)
                    i = i + str(1)
                    playsound(file_name)

def reply_mail(msg_id, message):
    global i,s
    TO_ADDRESS = message['From']
    FROM_ADDRESS = addr
    msg = email.mime.multipart.MIMEMultipart()
    msg['to'] = TO_ADDRESS
    msg['from'] = FROM_ADDRESS
    msg['subject'] = message['Subject']
    msg.add_header('In-Reply-To', msg_id)
    flag = True
    while(flag):
        texttospeech("Enter body.", file + i)
        i = i + str(1)
        body = speechtotext(20)
        print(body)
        try:
            msg.attach(MIMEText(body, 'plain'))
            s.sendmail(msg['from'], msg['to'], msg.as_string())
            texttospeech("Your reply has been sent successfully.", file + i)
            i = i + str(1)
            flag = False
        except:
            texttospeech("Your reply could not be sent. Do you want to try again? Say yes please or no.", file + i)
            i = i + str(1)
            act = speechtotext(3)
            act = act.lower()
            if act != 'yes please':
                flag = False

def frwd_mail(item, message):
    global i,s
    flag1 = True
    flag = True
    global i
    newtoaddr = list()
    while flag:
        while flag1:
            while True:
                texttospeech("Enter receiver's email address", file + i)
                i = i + str(1)
                to = speechtotext(15)
                texttospeech("You meant " + to + " say yes please to confirm or no to enter again", file + i)
                i = i + str(1)
                yn = speechtotext(3)
                yn = yn.lower()
                if yn == 'yes please':
                    to = to.strip()
                    to = to.replace(' ', '')
                    to = to.lower()
                    to = convert_special_char(to)
                    print(to)
                    newtoaddr.append(to)
                    break
            texttospeech("Do you want to add more recepients?", file + i)
            i = i + str(1)
            ans1 = speechtotext(3)
            ans1 = ans1.lower()
            print(ans1)
            if ans1 == "no" :
                flag1 = False

        message['From'] = addr
        message['To'] = ",".join(newtoaddr)
        try:
            s.sendmail(addr, newtoaddr, message.as_string())
            texttospeech("Your mail has been forwarded successfully.", file + i)
            i = i + str(1)
            flag = False
        except:
            texttospeech("Your mail could not be forwarded. Do you want to try again? Say yes please or no.", file + i)
            i = i + str(1)
            act = speechtotext(3)
            act = act.lower()
            if act != 'yes please':
                flag = False

def read_mails(mail_list, folder):
    global s, i
    mail_list.reverse()
    mail_count = 0
    to_read_list = list()
    for item in mail_list:
        result, email_data = conn.fetch(item, '(RFC822)')
        raw_email = email_data[0][1].decode()
        message = email.message_from_string(raw_email)
        To = message['To']
        From = message['From']
        Subject = message['Subject']
        Msg_id = message['Message-ID']
        texttospeech("Email number " + str(mail_count + 1) + "    .The mail is from " + From + " to " + To + "  . The subject of the mail is " + Subject, file + i)
        i = i + str(1)
        print('message id= ', Msg_id)
        print('From :', From)
        print('To :', To)
        print('Subject :', Subject)
        print("\n")
        to_read_list.append(Msg_id)
        mail_count = mail_count + 1

    flag = True
    while flag:
        n = 0
        flag1 = True
        while flag1:
            texttospeech("Enter the email number of the mail you want to read.", file + i)
            i = i + str(1)
            # Modified part:  get the user's input as a string and try to extract a number
            n_str = speechtotext(5)
            print(n_str)
            try:
                # Extract number from the string using regular expression
                match = re.search(r'\d+', n_str)
                if match:
                    n = int(match.group(0))
                    if 1 <= n <= mail_count:
                        texttospeech("You meant " + str(n) + ". Say yes please or no.", file + i)
                        i = i + str(1)
                        say = speechtotext(2)
                        say = say.lower()
                        if say == 'yes please':
                            flag1 = False
                    else:
                        texttospeech("Please enter a valid email number between 1 and " + str(mail_count) + ".", file + i)
                        i = i + str(1)
                else:
                    texttospeech("Please enter a valid number.", file + i)
                    i = i + str(1)

            except ValueError:
                texttospeech("Please enter a valid number.", file + i)
                i = i + str(1)

        msgid = to_read_list[n - 1]
        print("message id is =", msgid)
        typ, data = conn.search(None, '(HEADER Message-ID "%s")' % msgid)
        data = data[0]
        result, email_data = conn.fetch(data, '(RFC822)')
        raw_email = email_data[0][1].decode()
        message = email.message_from_string(raw_email)
        To = message['To']
        From = message['From']
        Subject = message['Subject']
        Msg_id = message['Message-ID']
        print('From :', From)
        print('To :', To)
        print('Subject :', Subject)
        texttospeech("The mail is from " + From + " to " + To + "  . The subject of the mail is " + Subject, file + i)
        i = i + str(1)
        Body = get_body(message)
        Body = Body.decode()
        Body = re.sub('<.*?>', '', Body)
        Body = os.linesep.join([s for s in Body.splitlines() if s])
        if Body != '':
            texttospeech(Body, file + i)
            i = i + str(1)
        else:
            texttospeech("Body is empty.", file + i)
            i = i + str(1)
        get_attachment(message)

        if folder == 'inbox':
            texttospeech("Do you want to reply to this mail? Say yes please or no. ", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            print(ans)
            if ans == "yes please":
                reply_mail(Msg_id, message)

        if folder == 'inbox' or folder == 'sent':
            texttospeech("Do you want to forward this mail to anyone? Say yes please or no. ", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            print(ans)
            if ans == "yes please":
                frwd_mail(Msg_id, message)

        if folder == 'inbox' or folder == 'sent':
            texttospeech("Do you want to delete this mail? Say yes please or no. ", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            print(ans)
            if ans == "yes please":
                try:
                    conn.store(data, '+X-GM-LABELS', '\\Trash')
                    conn.expunge()
                    texttospeech("The mail has been deleted successfully.", file + i)
                    i = i + str(1)
                    print("mail deleted")
                except:
                    texttospeech("Sorry, could not delete this mail. Please try again later.", file + i)
                    i = i + str(1)

        if folder == 'trash':
            texttospeech("Do you want to delete this mail? Say yes please or no. ", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            print(ans)
            if ans == "yes please":
                try:
                    conn.store(data, '+FLAGS', '\\Deleted')
                    conn.expunge()
                    texttospeech("The mail has been deleted permanently.", file + i)
                    i = i + str(1)
                    print("mail deleted")
                except:
                    texttospeech("Sorry, could not delete this mail. Please try again later.", file + i)
                    i = i + str(1)

        texttospeech("Email ends here.", file + i)
        i = i + str(1)
        texttospeech("Do you want to read more mails?", file + i)
        i = i + str(1)
        ans = speechtotext(2)
        ans = ans.lower()
        if ans == "no":
            flag = False
def search_specific_mail(folder,key,value,foldername):
    global i, conn
    conn.select(folder)
    result, data = conn.search(None,key,'"{}"'.format(value))
    mail_list=data[0].split()
    if len(mail_list) != 0:
        texttospeech("There are " + str(len(mail_list)) + " emails with this email ID.", file + i)
        i = i + str(1)
    if len(mail_list) == 0:
        texttospeech("There are no emails with this email ID.", file + i)
        i = i + str(1)
    else:
        read_mails(mail_list,foldername)

def inbox_view(request):
    global i, addr, passwrd, conn
    if request.method == 'POST':
        print("clicked inbox")
        imap_url = 'imap.gmail.com'
        conn = imaplib.IMAP4_SSL(imap_url)
        conn.login(addr, passwrd)
        conn.select('"INBOX"')
        result, data = conn.search(None, '(UNSEEN)')
        unread_list = data[0].split()
        no = len(unread_list)
        result1, data1 = conn.search(None, "ALL")
        mail_list = data1[0].split()
        print("inbox")
        text = "You have reached your inbox. There are " + str(len(mail_list)) + " total mails in your inbox. You have " + str(no) + " unread emails" + ". To read unread emails say unread. To search a specific email say search. To go back to the menu page say back. To logout say logout."
        texttospeech(text, file + i)
        i = i + str(1)
        flag = True
        while(flag):
            act = speechtotext(5)
            act = act.lower()
            print(act)
            if act == 'unread':
                flag = False
                if no!=0:
                    read_mails(unread_list,'inbox')
                else:
                    texttospeech("You have no unread emails.", file + i)
                    i = i + str(1)
            elif act == 'search' or act=='such':
                flag = False
                emailid = ""
                while True:
                    texttospeech("Enter email ID of the person who's email you want to search.", file + i)
                    i = i + str(1)
                    emailid = speechtotext(15)
                    texttospeech("You meant " + emailid + " say yes please to confirm or no to enter again", file + i)
                    i = i + str(1)
                    yn = speechtotext(5)
                    yn = yn.lower()
                    if yn == 'yes please':
                        break
                emailid = emailid.strip()
                emailid = emailid.replace(' ', '')
                emailid = emailid.lower()
                emailid = convert_special_char(emailid)
                search_specific_mail('INBOX', 'FROM', emailid,'inbox')

            elif act == 'back':
                texttospeech("You will now be redirected to the menu page.", file + i)
                i = i + str(1)
                conn.logout()
                return JsonResponse({'result': 'success'})

            elif act == 'log out':
                addr = ""
                passwrd = ""
                texttospeech("You have been logged out of your account and now will be redirected back to the login page.", file + i)
                i = i + str(1)
                return JsonResponse({'result': 'logout'})

            else:
                texttospeech("Invalid action. Please try again.", file + i)
                i = i + str(1)

            texttospeech("If you wish to do anything else in the inbox or logout of your mail say yes please or else say no.", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            if ans == 'yes please':
                flag = True
                texttospeech("Enter your desired action. Say unread, search, back or logout. ", file + i)
                i = i + str(1)
        texttospeech("You will now be redirected to the menu page.", file + i)
        i = i + str(1)
        conn.logout()
        return JsonResponse({'result': 'success'})

    elif request.method == 'GET':
        return render(request, 'inbox.html')

def sent_view(request):
    global i, addr, passwrd, conn
    if request.method == 'POST':
        imap_url = 'imap.gmail.com'
        conn = imaplib.IMAP4_SSL(imap_url)
        conn.login(addr, passwrd)
        conn.select('"[Gmail]/Sent Mail"')
        result1, data1 = conn.search(None, "ALL")
        mail_list = data1[0].split()
        text = "You have reached your sent mails folder. You have " + str(len(mail_list)) + " mails in your sent mails folder. To search a specific email say search. To go back to the menu page say back. To logout say logout."
        texttospeech(text, file + i)
        i = i + str(1)
        flag = True
        while (flag):
            act = speechtotext(5)
            act = act.lower()
            print(act)
            if act == 'search' or act=="such":
                flag = False
                emailid = ""
                while True:
                    texttospeech("Enter email ID of receiver.", file + i)
                    i = i + str(1)
                    emailid = speechtotext(15)
                    texttospeech("You meant " + emailid + " say yes please to confirm or no to enter again", file + i)
                    i = i + str(1)
                    yn = speechtotext(5)
                    yn = yn.lower()
                    if yn == 'yes please':
                        break
                emailid = emailid.strip()
                emailid = emailid.replace(' ', '')
                emailid = emailid.lower()
                emailid = convert_special_char(emailid)
                search_specific_mail('"[Gmail]/Sent Mail"', 'TO', emailid,'sent')

            elif act == 'back':
                texttospeech("You will now be redirected to the menu page.", file + i)
                i = i + str(1)
                conn.logout()
                return JsonResponse({'result': 'success'})

            elif act == 'logout':
                addr = ""
                passwrd = ""
                texttospeech("You have been logged out of your account and now will be redirected back to the login page.", file + i)
                i = i + str(1)
                return JsonResponse({'result': 'logout'})

            else:
                texttospeech("Invalid action. Please try again.", file + i)
                i = i + str(1)

            texttospeech("If you wish to do anything else in the sent mails folder or logout of your mail say yes please or else say no.", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            if ans == 'yes please':
                flag = True
                texttospeech("Enter your desired action. Say search, back or logout. ", file + i)
                i = i + str(1)
        texttospeech("You will now be redirected to the menu page.", file + i)
        i = i + str(1)
        conn.logout()
        return JsonResponse({'result': 'success'})

    elif request.method == 'GET':
        return render(request, 'sent.html')

def trash_view(request):
    global i, addr, passwrd, conn
    if request.method == 'POST':
        print("clicked trash")
        conn.login(addr, passwrd)
        res,mailbox=conn.list()
        print(mailbox)
        conn.select('"[Gmail]/Bin"')
        result1, data1 = conn.search(None, "ALL")
        mail_list = data1[0].split()
        text = "You have reached your trash folder. You have " + str(len(mail_list)) + " mails in your trash folder. To search a specific email say search. To go back to the menu page say back. To logout say logout."
        texttospeech(text, file + i)
        i = i + str(1)
        flag = True
        while (flag):
            act = speechtotext(5)
            act = act.lower()
            print(act,"====")
            if act == 'search' or act=='such':
                print(act)
                flag = False
                emailid = ""
                while True:
                    texttospeech("Enter email ID of sender.", file + i)
                    i = i + str(1)
                    emailid = speechtotext(15)
                    texttospeech("You meant " + emailid + " say yes please to confirm or no to enter again", file + i)
                    i = i + str(1)
                    yn = speechtotext(5)
                    yn = yn.lower()
                    if yn == 'yes please':
                        break
                emailid = emailid.strip()
                emailid = emailid.replace(' ', '')
                emailid = emailid.lower()
                emailid = convert_special_char(emailid)
                search_specific_mail('"[Gmail]/Bin"', 'FROM', emailid, 'trash')

            elif act == 'back' or act=='bak':
                print(act)
                texttospeech("You will now be redirected to the menu page.", file + i)
                i = i + str(1)
                conn.logout()
                return JsonResponse({'result': 'success'})

            elif act == 'log out':
                addr = ""
                passwrd = ""
                texttospeech(
                    "You have been logged out of your account and now will be redirected back to the login page.",
                    file + i)
                i = i + str(1)
                return JsonResponse({'result': 'logout'})

            else:
                texttospeech("Invalid action. Please try again.", file + i)
                i = i + str(1)

            texttospeech("If you wish to do anything else in the trash folder or logout of your mail say yes please or else say no.", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            print(ans)
            if ans == 'yes please':
                flag = True
                texttospeech("Enter your desired action. Say search, back or logout. ", file + i)
                i = i + str(1)
        texttospeech("You will now be redirected to the menu page.", file + i)
        i = i + str(1)
        conn.logout()
        return JsonResponse({'result': 'success'})
    elif request.method == 'GET':
        return render(request, 'trash.html')