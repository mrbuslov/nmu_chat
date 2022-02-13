import email
import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from matplotlib.style import context
from django.core import serializers
import json
from django.http import HttpResponse

from pytest import console_main

from account.models import Account
from chat.models import Message, Room, File

def index(request):
    if request.user.is_authenticated:
        users = Account.objects.filter(is_active=True).exclude(email=request.user)
        my_users = []
        
        for obj in users:
            if Room.objects.filter(Q(participant_1=request.user), Q(participant_2=obj)).exists() or Room.objects.filter(Q(participant_2=request.user), Q(participant_1=obj)).exists():
                my_users.append(obj.id)
            
        users = Account.objects.filter(id__in=my_users)
    else:
        # users = Account.objects.filter(is_active=True)
        return redirect('account:login')

    # для разнообразия фото профилей
    list_for_random = ['/static/img/user_blank_1.svg', '/static/img/user_blank_2.svg', '/static/img/user_blank_3.svg', '/static/img/user_blank_4.svg', '/static/img/user_blank_5.svg']
    return render(request, 'index.html', {'users':users, 'list_for_random': list_for_random, 'msgs':users})

# def room(request, room_name):
def room(request):

    if request.is_ajax:
        room_name = request.POST.get('user', None)


        if not Account.objects.filter(email=room_name).exists():
            return redirect('chat:index')


        participant = Account.objects.get(email=room_name)

        if Room.objects.filter(participant_1 = participant).exists() or Room.objects.filter(participant_2 = participant).exists():
            if Room.objects.filter(Q(participant_1 = participant),Q(participant_2 = request.user)).exists():
                room_name = Room.objects.get(Q(participant_1 = participant),Q(participant_2 = request.user)).name
            elif Room.objects.filter(Q(participant_2 = participant),Q(participant_1 = request.user)).exists():
                room_name = Room.objects.get(Q(participant_2 = participant),Q(participant_1 = request.user)).name
        else:
            room_name = str(uuid.uuid4()).replace('-','')
            Room.objects.create(name=room_name, participant_1=participant, participant_2=request.user)

        # context = {
        #     'room_name': room_name, 
        #     'messages': Message.objects.filter(room=Room.objects.get(name=room_name))
        #     }
        # return render(request, 'chatroom.html', context)

        if Message.objects.filter(room=Room.objects.get(name=room_name)).exists():
            msg_obj = Message.objects.filter(room=Room.objects.get(name=room_name))
            msg_obj_json=serializers.serialize('json',msg_obj)
        else:
            msg_obj_json = serializers.serialize('json',{})
        return JsonResponse(data={
            'posts':msg_obj_json,
        })



def get_room(request):
    get_chat = request.POST.get('receiver', None)
    if Account.objects.filter(email=get_chat).exists():
        participant = Account.objects.get(email=get_chat)
        # if Room.objects.filter(participant_1 = participant).exists() or Room.objects.filter(participant_2 = participant).exists():
        if Room.objects.filter(Q(participant_1 = participant),Q(participant_2 = request.user)).exists():
            room = Room.objects.get(Q(participant_1 = participant),Q(participant_2 = request.user)).name
        elif Room.objects.filter(Q(participant_2 = participant),Q(participant_1 = request.user)).exists():
            room = Room.objects.get(Q(participant_2 = participant),Q(participant_1 = request.user)).name
        else:
            room = str(uuid.uuid4()).replace('-','')
            Room.objects.create(name=room, participant_1=participant, participant_2=request.user)

        return JsonResponse(data={
            'room':room,
            'sender':request.user.email,
            'searched_user': list(Account.objects.filter(email=get_chat).values()),
            'online': participant.online,
            'last_online': participant.last_online,
        })
    else:
        return redirect('chat:index')
    


def show_chats(request):
    if request.is_ajax():
        searchInput = request.GET.get('search_user', None)
        
        if searchInput is not None and searchInput != "":
            user = Account.objects.filter(Q(email__icontains = searchInput)|Q(first_name__icontains = searchInput)|Q(last_name__icontains = searchInput)|Q(username__icontains = searchInput)).exclude(email=request.user).values()
            # user_json = serializers.serialize('json',user)
        else:
            user = Account.objects.filter(is_active=True).exclude(email=request.user)
            my_users = []
            
            for obj in user:
                if Room.objects.filter(Q(participant_1=request.user), Q(participant_2=obj)).exists() or Room.objects.filter(Q(participant_2=request.user), Q(participant_1=obj)).exists():
                    my_users.append(obj.id)
                
            user = Account.objects.filter(id__in=my_users).values()
        return JsonResponse({'data':list(user)}, safe=False)

def get_last_msg(request):
    if request.is_ajax():
        this_user = request.GET.get('this_user', None)

        if Message.objects.filter(Q(sender=request.user, receiver=Account.objects.get(email=this_user)) | Q(sender=Account.objects.get(email=this_user), receiver=request.user)).exists():
            last_msg = Message.objects.filter(Q(sender=request.user, receiver=Account.objects.get(email=this_user)) | Q(sender=Account.objects.get(email=this_user), receiver=request.user)).last()
            last_msg = last_msg.value.replace('\\n','').replace('\n','')
        else:
            last_msg = '...'
        return JsonResponse(last_msg, safe=False)


    
def upload_my_img(request):
    if request.method == 'POST':
        if request.is_ajax():
            image = request.FILES.get('img')
            uploaded_image = Account.objects.get(email=request.user.email)
            uploaded_image.image=image
            uploaded_image.save()
            response_data = {
                'url': uploaded_image.image.url,
            }
    return HttpResponse(json.dumps(response_data))


def update_data(request):
    if request.method == 'POST' and request.is_ajax():
        my_name = request.POST.get('my_name', None)
        my_surname = request.POST.get('my_surname', None)
        my_phone_num = request.POST.get('my_phone_num', None)
        left_handed_checked = request.POST.get('left_handed_checked', None)

        user = request.user

        if my_name != None:
            user.first_name = my_name
            user.save()
        if my_surname != None:
            user.last_name = my_surname
            user.save()
        if my_phone_num != None:
            user.phone_number = my_phone_num
            user.save()
        if left_handed_checked != None:
            if left_handed_checked == 'true':
                user.left_handed = True
                user.save()
            else:
                user.left_handed = False
                user.save()
        
    return HttpResponse(json.dumps('ok'))

def get_settings_data(request):
    if request.method == 'GET' and request.is_ajax():
        name = request.user.first_name
        surname = request.user.last_name
        phone_num = request.user.phone_number
        left_handed = request.user.left_handed

        data={}

        if name != None and name != '':
            data['my_name'] = name
        if surname != None and surname != '':
            data['my_surname'] = surname
        if phone_num != None and phone_num != '':
            data['my_phone_num'] = phone_num
        if left_handed == True:
            data['left_handed'] = left_handed

        return HttpResponse(json.dumps(data))


def upload_file_to_chat(request):
    if request.method == 'POST' and request.is_ajax():
        files = request.FILES.getlist('img')
        files_list = []
        for val in files:
            name = File.objects.create(file=val, user=request.user)
            files_list.append(name)
    
        files_list = serializers.serialize('json',files_list)
        return JsonResponse(data={
            'files':files_list,
        })