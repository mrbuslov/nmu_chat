import locale
import uuid
from django.http import HttpResponse, JsonResponse
from account.models import Account
from .models import Room, Message
from django.db.models import Q
from .models import File
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
host = 'http://127.0.0.1/'

def app_index(request):
    user_email = request.GET.get('user_email', None)

    user_id = None
    # chat
    all_users = []
    # settings
    my_img_link = None
    my_email = None
    my_name = None
    my_surname = None
    my_phone = None


    if Account.objects.filter(email=user_email).exists():
        if Account.objects.get(email=user_email).is_active == False:
            user_id = 'not_active'
        else:
            users = Account.objects.filter(is_active=True).exclude(email=user_email)
            this_user = Account.objects.get(email=user_email)
            participants_ids = []
            
            for this_participant in users:
                if Room.objects.filter(Q(participant_1=this_user), Q(participant_2=this_participant)).exists() or Room.objects.filter(Q(participant_2=this_user), Q(participant_1=this_participant)).exists():
                    participants_ids.append(this_participant.id)
                
            users = Account.objects.filter(id__in=participants_ids)
            for user in users:
                participant_id = user.pk
                if user.first_name != None and user.last_name != None and user.first_name != '' and user.last_name != '':
                    participant_name = user.first_name + ' ' + user.last_name
                elif user.first_name != None and user.first_name != '':
                    participant_name = user.first_name
                else:
                    participant_name = user.email

                if user.image != None and user.image != '':
                    participant_img_link = host + str(user.image)
                else:
                    participant_img_link = host + 'static/img/user_blank.svg'

                all_users.append({
                    'participant_id': participant_id,
                    'participant_img_link': participant_img_link,
                    'participant_name': participant_name,
                })

            my_img_link = host + str(this_user.image)
            my_email = this_user.email
            my_name = this_user.first_name
            my_surname = this_user.last_name
            my_phone = this_user.phone_number
    else:
        user_id = 'not_exists'
    
    responseData = {
        'data': user_id, 
        'all_users':all_users,
        'my_img_link':my_img_link,
        'my_email': my_email,
        'my_name': my_name,
        'my_surname': my_surname,
        'my_phone': my_phone,
    }

    return JsonResponse(responseData)

def return_room_name(request):
    this_user = Account.objects.get(email=request.GET.get('this_user', None))
    try:
        this_participant = Account.objects.get(id=request.GET.get('this_participant', None))
    except:
        this_participant = Account.objects.get(email=request.GET.get('this_participant', None))

    print(this_participant.email)

    if Room.objects.filter(Q(participant_1 = this_user),Q(participant_2 = this_participant)).exists():
        room = Room.objects.get(Q(participant_1 = this_user),Q(participant_2 = this_participant)).name
    elif Room.objects.filter(Q(participant_2 = this_user),Q(participant_1 = this_participant)).exists():
        room = Room.objects.get(Q(participant_2 = this_user),Q(participant_1 = this_participant)).name
    else:
        room = str(uuid.uuid4()).replace('-','')
        Room.objects.create(name=room, participant_1=this_participant, participant_2=this_user)

    message_info = []
    if Message.objects.filter(room=Room.objects.get(name=room)).exists():
        msg_obj = Message.objects.filter(room=Room.objects.get(name=room))

        for obj in msg_obj:
            message_info.append({
                'message_id': obj.id,
                'message_text': obj.value,
                'message_date': obj.date,
                'message_sender': obj.sender,
                'message_receiver': obj.receiver,
            })

    if this_participant.first_name != None and this_participant.last_name != None and this_participant.first_name != '' and this_participant.last_name != '':
        participant_name = this_participant.first_name + ' ' + this_participant.last_name
    elif this_participant.first_name != None and this_participant.first_name != '':
        participant_name = this_participant.first_name
    else:
        participant_name = this_participant.email

    last_online = this_participant.last_online
    if last_online == None or last_online == '':
        online = 'был(а) давно'
    else:
        locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
        now = datetime.now()

        last_online_time = str(last_online.time().strftime("%H:%M"))
        last_online_date = last_online.day 
        
        if last_online_date == now.day:
            online = 'был(а) в ' + last_online_time
        elif last_online_date - now.day == 1:
            online = 'был(а) вчера в ' + last_online_time
        else:
            online = 'был(а) '+ str(last_online.strftime("%d %B")) +' в ' + last_online_time



    data = {
        'room':room,
        'message_info': message_info,
        'participant_name': participant_name,
        'participant_online': online,
        'this_participant': this_participant.email,
    }
    return JsonResponse(data)

def get_messages(request):
    this_user = Account.objects.get(email=request.GET.get('this_user_email', None))
    this_participant = Account.objects.get(id = request.GET.get('participant_id', None))

    room = return_room_name({
        'this_user': this_user.email,
        'this_participant': this_participant.email
    })
    print(room)


@csrf_exempt
def app_upload_file(request):
    data = request.POST.dict()

    if Account.objects.filter(email = data['email']).exists():
        this_person = Account.objects.get(email = data['email'])
        file = request.FILES.getlist('media')
        file_obj = File.objects.create(file=file[0], user=this_person, this_name=data['filename'])
        
        _type = None
        if str(file_obj.file).lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            _type = 'image'
        elif str(file_obj.file).lower().endswith(('.mp3', '.wav', '.aac')):
            _type = 'music'
        else:
            _type = 'file'

        return JsonResponse({'response': host+str(file_obj.file), 'type': _type})
    else:
        return JsonResponse({'response':'error'})


def get_settings(request):
    this_user = Account.objects.get(email=request.GET.get('email', None))
    
    if this_user.image == None or this_user.image == '':
        image = host + 'static/img/user_blank.svg'
    else:
        image = host + str(this_user.image)
    
    if this_user.first_name == None:
        first_name = ''
    else:
        first_name = this_user.first_name
    if this_user.last_name == None:
        surname = ''
    else:
        surname = this_user.last_name
    if this_user.phone_number == None:
        phone_number = ''
    else:
        phone_number = this_user.phone_number


    context = {
        'image': image,
        'email': this_user.email,
        'first_name': first_name,
        'surname': surname,
        'phone_number': phone_number,
    }
    
    return JsonResponse(context)

@csrf_exempt
def update_settings(request):
    data = request.POST.dict()
    this_user = Account.objects.get(email=data['this_user'])

    this_user.first_name = data['name']
    this_user.last_name = data['surname']
    this_user.phone_number = data['phone']
    this_user.save()
    
    return HttpResponse('ok')



@csrf_exempt
def app_upload_file(request):
    data = request.POST.dict()

    if Account.objects.filter(email = data['email']).exists():
        this_person = Account.objects.get(email = data['email'])
        file = request.FILES.getlist('media')
        this_person.image = file=file[0]
        this_person.save()
        

        return JsonResponse({'response': host+str(this_person.image)})
    else:
        return JsonResponse({'response':'error'})

from django.contrib.auth import authenticate
def app_login(request):
    try:
        this_user = Account.objects.get(email=request.GET.get('email', None))
        user = authenticate(email=request.GET.get('email', None), password=request.GET.get('password', None))
        if user == None:
            return JsonResponse({'response':'error'})
        return JsonResponse({'response':this_user.email})
    except:
        return JsonResponse({'response':'error'})


from django.core.mail import EmailMultiAlternatives
from account.views import EmailThreading
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse, reverse_lazy
from account.utils import token_generator
from website import settings
@csrf_exempt
def app_register(request):
    try:
        data = request.POST.dict()

        email = data['email']
        password = data['password']

        if Account.objects.filter(email=email).exists():
            return JsonResponse({'response':'exists'})

        user = Account.objects.create_user(password=password, email=email.lower())
        user.is_active = False # Меняем на True после регистрации
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        domain = get_current_site(request).domain
        link = reverse('account:activate', kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

        activate_url='http://' + domain + link
        mail_title = "Активация"
        variables = {
            'activate_url': activate_url,
        }
        html = get_template('registration/email.html').render(variables)
        text = f'{activate_url}'
        
        msg = EmailMultiAlternatives(
            mail_title,
            text,
            settings.EMAIL_HOST_USER,
            [email])
        msg.attach_alternative(html, "text/html")
        # msg.send(fail_silently=False) 
        EmailThreading(msg).start()

        return JsonResponse({'response':'ok'})
    except:
        return JsonResponse({'response':'error'})
    

def app_get_users(request):
    this_user = Account.objects.get(email=request.GET.get('this_user', None))
    searched_user = request.GET.get('searched_user', None).lower()
    users_list = []

    users = Account.objects.filter(Q(email__icontains = searched_user)|Q(first_name__icontains = searched_user)|Q(last_name__icontains = searched_user)|Q(username__icontains = searched_user)).exclude(email=this_user)
    users_query = []
    for us in users:
        users_query.append(us)
    


    for user in users_query:
        if Room.objects.filter(Q(participant_1=this_user), Q(participant_2=user)).exists() or Room.objects.filter(Q(participant_2=this_user), Q(participant_1=user)).exists():
            if user.image != None and user.image != '':
                user_img_link = host + str(user.image)
            else:
                user_img_link = host + 'static/img/user_blank.svg'
            users_list.append(
                {
                    'user_email': user.email,
                    'user_id': user.id,
                    'user_img_link': user_img_link,
                }
            )
            users_query.remove(user)

    for user in users_query:
        print(user.image == '')
        if user.image != None and user.image != '':
            user_img_link = host + str(user.image)
        else:
            user_img_link = host + 'static/img/user_blank.svg'
        users_list.append(
                {
                    'user_email': user.email,
                    'user_id': user.id,
                    'user_img_link': user_img_link,
                }
            )

    

    return JsonResponse({'users_list':users_list})