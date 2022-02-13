from django.shortcuts import render
from account.models import Account
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout

from django.core.mail import EmailMessage
from django.template.loader import get_template, render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.conf import settings

from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
import re


import threading
# view для того, чтобы быстрее отправлять email
class EmailThreading(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()



@login_required(login_url='/login/')
def profile(request):
    board_obj = Board.objects.filter(author=request.user) 
    time_now1 = str(datetime.today().date().day)
    time_now2 = str(datetime.today().date().day-1)

    
    current_lang = get_language() # для того, чтобы установить в шаблоне html ru или html uk 

    context={
        'board_obj':board_obj,
        'time_now1':time_now1,
        'time_now2':time_now2,
        'current_lang':current_lang,
    }

    return render(request, 'user/profile.html', context)

from django.db.models import Q
def account_profile(request, username):
    if Account.objects.filter(username=username).exists():
        board_obj = Board.objects.filter(Q(author=Account.objects.get(username=username).pk), Q(status='published')|Q(status='24hour'))
        user=Account.objects.get(username=username)
        time_now1 = str(datetime.today().date().day)
        time_now2 = str(datetime.today().date().day-1)

        current_lang = get_language() # для того, чтобы установить в шаблоне html ru или html uk 

        context={
            'board_obj':board_obj,
            'requested_user':user,
            'time_now1':time_now1,
            'time_now2':time_now2,
            'current_lang':current_lang,
        }

        if user == request.user:
            return redirect('/profile/')


        return render(request, 'user/account.html', context)
    else:
        return HttpResponse('Такий Юзер зник о_о')


def registration(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if Account.objects.filter(email=email).exists():
            return redirect('account:registration')



        user = Account.objects.create_user(password=password, email=email.lower())
        user.is_active = False # Меняем на True после регистрации
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        domain = get_current_site(request).domain
        link = reverse('account:activate', kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

        activate_url='http://' + domain + link

        # email_context = {
        #     'user':user,
        #     'activate_url': activate_url,
        # }

        # email_subject = 'Активация профиля'
        # # email_body = 'Здравствуй, ' + user.username + '! Используйте эту ссылку, чтобы подтвердить Ваш аккаунт\n' + activate_url # email_body = render_to_string('registration/email.html')
        # email_body = render_to_string('registration/email.html', email_context)
        # email_msg = EmailMessage(
        #     email_subject,
        #     email_body,
        #     settings.EMAIL_HOST_USER,
        #     [email],
        # )

        # # email_msg.send(fail_silently=False) 

        # EmailThreading(email_msg).start()








        mail_title = "Активация"
        variables = {
            'activate_url': activate_url,
        }
        html = get_template('registration/email.html').render(variables)
        # text = get_template('registration/email.html').render(variables)
        text = f'https://drive.google.com/uc?id=16rUVLcPvql3LBz-hbSB9u5BFO1fgMznU - ( наше лого :) )\nДавайте підтвердимо Ваш аккаунт\nЩоб почати користуватися Teenwork, просто натисніть кнопку підтвердження адреси електронної пошти нижче:\nПідтвердити\n{activate_url}\nУ вас є питання? Подивіться тут.\nhttps://teenwork.com.ua/rules/\nTeenwork - платформа, де підлітки і не тільки можуть знайти роботу, яка їм до вподоби.'
        
        msg = EmailMultiAlternatives(
            mail_title,
            text,
            settings.EMAIL_HOST_USER,
            [email])
        msg.attach_alternative(html, "text/html")
        # msg.send(fail_silently=False) 
        EmailThreading(msg).start()
        

        return render(request, 'registration/registration_success.html', {'email':email, 'current_lang':get_language()})
    # else:
    #     return render(request, 'registration/registration.html', {'current_lang':get_language()})

def resend_activation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = Account.objects.get(email=email)

        uidb64 =urlsafe_base64_encode(force_bytes(user.pk))

        domain = get_current_site(request).domain
        link = reverse('account:activate', kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

        activate_url='http://' + domain + link


        mail_title = "Активация"
        variables = {
            'activate_url': activate_url,
        }
        html = get_template('registration/email.html').render(variables)
        text = f'https://drive.google.com/uc?id=16rUVLcPvql3LBz-hbSB9u5BFO1fgMznU - ( наше лого :) )\nДавайте підтвердимо Ваш аккаунт\nЩоб почати користуватися Teenwork, просто натисніть кнопку підтвердження адреси електронної пошти нижче:\nПідтвердити\n{activate_url}\nУ вас є питання? Подивіться тут.\nhttps://teenwork.com.ua/rules/\nTeenwork - платформа, де підлітки і не тільки можуть знайти роботу, яка їм до вподоби.'
        
        msg = EmailMultiAlternatives(
            mail_title,
            text,
            settings.EMAIL_HOST_USER,
            [email])
        msg.attach_alternative(html, "text/html")
        EmailThreading(msg).start()
        

        return render(request, 'registration/resend_activation_email_success.html', {'current_lang':get_language()})
    else:
        return render(request, 'registration/resend_activation_email.html', {'current_lang':get_language()})




from django.views.generic import View
class VerificationView(View):
    def get(self,request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
        except Exception as e:
            user = None
        
        if user is not None:
            if not token_generator.check_token(user,token):
                return redirect('account:login' + '?message= ' + 'Пользователь уже активирован')


            if user.is_active:
                return redirect('account:login')
            user.is_active = True
            user.save()

            return redirect('account:login')
        else:
            raise Exception


def user_login(request):
    if request.user.is_authenticated:
        return redirect('chat:index')
    else:
        if request.method == 'POST':

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(email=email, password=password)
                
            if user is not None:
                if user.is_blocked:
                    return redirect('account:logout')
                login(request, user)
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('chat:index')
            else:  
                return render(request, 'registration/login.html')
        else:  
            return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    return redirect('chat:index')


from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
class PasswordResetPSWRDView(PasswordResetView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('account:password_reset_done')



from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required(login_url='/login/', redirect_field_name='/') # redirect_field_name - чтобы просто перенаправило на  главную, а не на ту же страницу
def favourite_add(request, pk):
    pk = int(pk)
    if request.user.is_authenticated:
        post = get_object_or_404(Board, id=pk)
        if post.favourites.filter(id=request.user.id).exists():
            post.favourites.remove(request.user)
        else:
            post.favourites.add(request.user)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    # else:
    #     return redirect('/login/')

@csrf_exempt
@login_required(login_url='/login/')
def favourite_list(request):
    new = Board.objects.filter(favourites=request.user)

    time_now1 = str(datetime.today().date().day)
    time_now2 = str(datetime.today().date().day-1)

    
    current_lang = get_language() # для того, чтобы установить в шаблоне html ru или html uk 

    context = {
        'new':new,
        'time_now1':time_now1,
        'time_now2':time_now2,
        'current_lang':current_lang,
    }

    return render(request, 'board/favourites.html', context)




from .forms import ProfileEditForm
@login_required(login_url='/login/')
@csrf_exempt 
def profile_edit(request):

    if request.is_ajax():
        data = request.POST.get('data', None)
        isTelegram = request.POST.get('isTelegram', None)

        
        tel = Telegram.objects.get(person = request.user)
        if data:
            if data == 'checked':
                tel.telegram = True
                data = 'true'
            else:
                tel.telegram = False
                data = 'false'
            tel.save()
            return JsonResponse(data, safe=False)
        elif isTelegram:
            if tel.telegram == True:
                isTelegram = 'true'
            else:
                isTelegram = 'false'
            return JsonResponse(isTelegram, safe=False)


    username = request.user.username
    account = Account.objects.get(username=username) 
    form = ProfileEditForm(instance=account)
    if request.method == 'POST' and 'profile_edit_btn' in request.POST:
        form = ProfileEditForm(request.POST, instance=account)
        if form.is_valid():
            post = form.save(commit=False)
            if request.FILES.get('img'):
                post.image = request.FILES.get('img')
            post.save()
        return redirect('account:profile_edit')

    tlg_obj = Telegram.objects.get(person=request.user)
    tlg_form = TelegramForm(instance=tlg_obj)
    if request.method =='POST' and 'tlg_btn' in request.POST:
        tlg_form = TelegramForm(request.POST, instance=tlg_obj)
        if tlg_form.is_valid():
            tel = tlg_form.save(commit=False)
            tel.person = request.user
            tlg_form.save()
            return redirect('account:profile_edit')
        else:  
            return redirect('account:profile_edit')

    if request.method == 'POST' and 'delete_account_btn' in request.POST:
        for board_obj in Board.objects.filter(author=request.user):
            board_obj.delete() # чтобы в Deleted Ads сохранить его опублик.объявл.
        Account.objects.get(id=request.user.id).delete()
        return redirect('board:index')

    current_lang = get_language() # для того, чтобы установить в шаблоне html ru или html uk 

    return render(request, 'user/profile_edit.html', {'form':form, 'account':account, 'tlg_form':tlg_form, 'current_lang':current_lang,})



class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'registration/reset_email.html', {'current_lang':get_language()})
    
    def post(self, request):
        email = request.POST.get('email', None)
        
        if email is None:
            # messages.error(request, 'Не забудьте вписать email')
            return render(request, 'registration/reset_email.html', {'current_lang':get_language()})

        user = Account.objects.filter(email=email)
        if user.exists():
            uidb64 =urlsafe_base64_encode(force_bytes(user[0].pk))

            domain = get_current_site(request).domain
            link = reverse('account:set_new_pswrd', kwargs={'uidb64':uidb64,'token':token_generator.make_token(user[0])})

            activate_url='http://' + domain + link

            # email_context = {
            #     'user':user,
            #     'activate_url': activate_url,
            # }

            # email_subject = 'Обновление пароля'
            # # email_body = 'Здравствуй, ' + user.username + '! Используйте эту ссылку, чтобы подтвердить Ваш аккаунт\n' + activate_url # email_body = render_to_string('registration/email.html')
            # email_body = render_to_string('registration/reset_password.html', email_context)
            # email_msg = EmailMessage(
            #     email_subject,
            #     email_body,
            #     settings.EMAIL_HOST_USER,
            #     [email],
            # )

            # # email_msg.send(fail_silently=False) 


            # EmailThreading(email_msg).start() # мы быстрее отправляем email





            mail_title = "Оновлення пароля"
            variables = {
                'activate_url': activate_url,
            }
            html = get_template('registration/reset_password.html').render(variables)
            text = f'https://drive.google.com/uc?id=16rUVLcPvql3LBz-hbSB9u5BFO1fgMznU - ( наше лого :) )\nЗабули пароль?\nЩоб скинути пароль, натисніть кнопку нижче.\nСкинути\n{activate_url}\nЯкщо Ви не бажаєте змінювати свій пароль або не запитували скидання паролю, Ви можете проігнорувати або видалити цей лист.\nTeenwork - платформа, де підлітки і не тільки можуть знайти роботу, яка їм до вподоби.'
            
            msg = EmailMultiAlternatives(
                mail_title,
                text,
                settings.EMAIL_HOST_USER,
                [email])
            msg.attach_alternative(html, "text/html")
            # msg.send(fail_silently=False) 
            EmailThreading(msg).start() # мы быстрее отправляем email


            return render(request, 'registration/reset_email_success.html', {'current_lang':get_language()})
        else:
            return redirect('/registration/')
    
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.translation import get_language
class SetNewPswrdView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token,
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = Account.objects.get(pk=user_id)

            if PasswordResetTokenGenerator().check_token(user, token):
                # Пароль кликают 2-ой раз, так нельзя. Отошлём на повторную отправку
                return render(request, 'registration/reset_email.html', {'current_lang':get_language()})
        except DjangoUnicodeDecodeError as identifier:
            return render(request, 'registration/reset_email.html', {'current_lang':get_language()})
        return render(request, 'registration/set_new_pswrd.html', context)
    
    def post(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token,
        }

        password = request.POST.get('password', None)
        if password is None or len(password) < 4 or len(password) > 20:
            return render(request, 'registration/set_new_pswrd.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = Account.objects.get(pk=user_id)
            user.set_password(password)
            user.is_active = True
            user.save()

            return redirect('/login/')
        except DjangoUnicodeDecodeError as identifier:
            return render(request, 'registration/set_new_pswrd.html', context)

