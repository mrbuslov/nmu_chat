// -------------------------------- ЗАГРУЗКА ФОТО и изменение в данных в настройках ------------------------------------------------------- */ -->


function getCookie(name) {
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
    }


document.querySelector('.main_img').addEventListener('click', function(e){
    $('.black_back').css('zIndex','10')
    $('.settings').css('zIndex','10')
    $('.black_back').css('opacity','1')
    $('.settings').css('opacity','1')
});
document.querySelector('.black_back').addEventListener('click', function(e){
    $('.black_back').css('opacity','0')
    $('.settings').css('opacity','0')
    setTimeout(function(){$('.black_back').css('zIndex','-1'); $('.settings').css('zIndex','-1')}, 700);
});



if(document.getElementById('my_img_file')){
  document.getElementById('my_img_file').onchange = function() {
      if (this.files[0]){
        document.querySelector('.big_img').style.opacity = '0.7';
        document.querySelector('.big_img').style.filter = 'blur(2px)';
        $('#myImageForm').submit();
      }
  };
}

document.getElementById('my_name').addEventListener('blur', function(e){
    $('#myDetails').submit();
});
document.getElementById('my_surname').addEventListener('blur', function(e){
    $('#myDetails').submit();
});
document.getElementById('my_phone_num').addEventListener('blur', function(e){
    $('#myDetails').submit();
});

document.getElementById('left_handed').addEventListener('click', function(e){
    var checked = '';

    if ($(this).is(':checked')){
		checked = true;
	} else {
		checked = false;
	}

    $.ajax({
        url: '/update_data/',
        type: 'POST',
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data: {'left_handed_checked':checked},
        success: function(data) {
            data = JSON.parse(data);
            $('.big_img').attr("src",data.url);
            document.querySelector('.big_img').style.opacity = '1';
            document.querySelector('.big_img').style.filter = 'initial';
        }
    });
});

$(document).ready(function() {
    $('#myImageForm').submit(function(e) {
        e.preventDefault(); 
        var data = new FormData($('#myImageForm').get(0));

        $.ajax({
            url: '/upload/',
            type: 'POST',
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            data: data,
            processData: false,
            contentType: false,
            success: function(data) {
                data = JSON.parse(data);
                $('.big_img').attr("src",data.url);
                document.querySelector('.big_img').style.opacity = '1';
                document.querySelector('.big_img').style.filter = 'initial';
            }
        });
        return false;
    });
});

$(document).ready(function() {
    $('#myDetails').submit(function(e) {
        e.preventDefault(); 
        var my_name = $('#my_name').val();
        var my_surname = $('#my_surname').val();
        var my_phone_num = $('#my_phone_num').val();

        $.ajax({
            url: '/update_data/',
            type: 'POST',
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            data: {
                'my_name': my_name,
                'my_surname': my_surname,
                'my_phone_num': my_phone_num,
            },
            success: function(data) {
                $('.changes_saved').css('opacity', 1)
                setTimeout(function(){$('.changes_saved').css('opacity', 0)}, 2000);
            }
        });
    });
});

$(document).ready(function() {
    $.ajax({
        url: '/get_settings_data/',
        type: 'GET',
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data: {
            'get_data': 'get_data',
        },
        success: function(data) {
            data = JSON.parse(data);
            
            if(data['my_name']){
                $('#my_name').val(data['my_name'])
            }
            if(data['my_surname']){
                $('#my_surname').val(data['my_surname'])
            }
            if(data['my_phone_num']){
                $('#my_phone_num').val(data['my_phone_num'])
            }
            if(data['left_handed']){
                $('#left_handed').prop('checked', true);
            }
        }
    });
});



// -----------------------------Поиск последнего отправленного сообщения польз. и добавление под именем в чате------------------------------------ -->

    $(document).ready(function(){
        $('#chats input').each(function(e){
            this_user = $(this).val();
            next_el = $(this).siblings('span');

            $.ajax({
                url: '/get_last_msg/',
                data: {
                    'this_user': this_user,
                },
                success: function(msg){
                    if(JSON.parse(msg).includes('class=\"chat_img\"')){
                        next_el.html('<i>Изображение</i>');
                    }
                    else if(JSON.parse(msg).includes('class=\"file_chat_img\"')){
                        next_el.html('<i>Файл</i>');
                    }
                    else{
                        next_el.text(msg.substring(1, msg.length-1)); // убираем кавычки
                    }
                },
                dataType: 'html',
                async: false,
            });
        });
    });

 // -------------------------------- ЗАГРУЗКА файлов в чат ------------------------------------------------------- */ -->
 

    var chatSocket;

    if(document.getElementById('files_upload')){
        document.getElementById('files_upload').onchange = function() {
            if (this.files[0]){
                // document.querySelector('.big_img').style.opacity = '0.7';
                // document.querySelector('.big_img').style.filter = 'blur(2px)';
                $('#fileForm').submit();
            }
        };
    }
    $('#fileForm').submit(function(e) {
        e.preventDefault(); 
        var file = new FormData($('#fileForm')[0]);

        var roomName = '';
        var sender_email = ''

        var user = $('.chat_name_field input').val();
        // просим у бекенда номер комнаты и свой email
        $.ajax({
            url:"/get_room/",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type:'post',
            async:false,
            data:{
                'receiver':user,
            },
            success:function(res){
                roomName = res.room;
                sender_email = res.sender;
            }
        });

        $.ajax({
            url: '/upload_file_to_chat/',
            type: 'POST',
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            data: file,
            processData: false,
            contentType: false,
            success: function(data) {
                
                // WebSocket.close();
                    // устанавливаем соединение
                // chatSocket = new WebSocket(
                //     'ws://' +
                //     window.location.host +
                //     '/ws/' +
                //     roomName +
                //     '/'
                // );

                var json_data=$.parseJSON(data.files);
                $.each(json_data,function(index,value){
                    var format = value.fields['file'].split('.')[value.fields['file'].split('.').length - 1]
                    var message = ''
                    if(format==='jpg'){ //  || format==='jpeg' || format==='raw' || format==='png' || format==='jfif'
                        message = '<img src="'+value.fields['file']+'" class="chat_img" alt="">';
                    }
                    else{
                        message = '<a href="'+value.fields['file']+'" target="_blank">'+
                                    '<div class="chat_file_msg">'+
                                        '<img src="static/img/chat_file.png" alt="" class="file_chat_img">'+
                                        '<span class="chat_filename">'+value.fields['this_name']+'</span>'+
                                    '</div>'+
                                '</a>';
                    }

                    
                    chatSocket.send(JSON.stringify({
                        'message': message,
                        'email': sender_email,
                        'roomName': roomName,
                    }));
                    
                });
            }
        });
        return false;
    });
//// -----------------------------Присоединение к комнате и отправка сообщения------------------------------------ -->
    var roomName = $(this).text();
    var sender_email = ''

    var time_options = {         ////// для нормального отображения времени
        hour: 'numeric',
        minute: 'numeric',
        timezone: 'UTC',
    };
    var day_options = {         ////// для нормального отображения даты
        month: 'long',
        day: 'numeric',
        timezone: 'UTC',
    };

    $(document).on("click", ".user_cover", function(e){
        $('.send_msg_forms').css('display', 'flex');
        var user = $(this).find( "input" ).val();
        $('.user_cover').css('background', 'initial')
        $(this).css('background', '#fff')
        if(chatSocket){
            chatSocket.close() // закрываем сокет. Так как мы сделали эту переменную глобальную, при новом открытии того же чата у нас возникает новый сокет. Из-за этого, отправив одно сообщение, мы якобы отправляем два
        }

        // просим у бекенда номер комнаты и свой email
        $.ajax({
            url:"/get_room/",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type:'post',
            data:{
              'receiver':user,
            },
            success:function(res){
                roomName = res.room;
                sender_email = res.sender;
                
                $('.chat_name_field input').val(user); // сначала присвоим email скрытому полю, чтобы работать с ним

                if(res.searched_user[0]['first_name'] !== null && res.searched_user[0]['first_name'] !== '' && res.searched_user[0]['last_name'] !== null && res.searched_user[0]['last_name'] !== ''){
                    user = res.searched_user[0]['first_name'] + ' ' + res.searched_user[0]['last_name'];
                }
                else if(res.searched_user[0]['first_name'] !== null && res.searched_user[0]['first_name'] !== ''){
                    user = res.searched_user[0]['first_name'];
                }

                $('.chat_name').text(user); // потом нормально переименуем пользователя

                online = '';
                if(res.online){
                    online = 'онлайн'
                }
                else{ 
                    if(res.last_online === null || res.last_online === ''){
                        online = 'был(а) давно';
                    }
                    else{
                        
                        var now = new Date().toLocaleString("ru", day_options);

                        last_online_time = new Date(res.last_online).toLocaleString("ru", time_options); 
                        last_online_date = new Date(res.last_online).toLocaleString("ru", day_options); 
                        if(parseInt(last_online_date) === parseInt(now)){
                            online = 'был(а) в ' + last_online_time;
                        }
                        else if (parseInt(now) - parseInt(last_online_date) === 1){
                            online = 'был(а) вчера в ' + last_online_time;
                        }
                        else{
                            online = 'был(а) '+ last_online_date +' в ' + last_online_time;
                        }
                    }
                }
                $('.online').text(online);
            },
            async: false
        });


        document.getElementById('mainForm').addEventListener('submit', function(e){
            e.preventDefault();
            document.querySelector('#submit').onclick();
        });

        document.querySelector('#submit').onclick = function (e) {
            const messageInputDom = document.querySelector('#input');
            const message = messageInputDom.value;
            if(message !== '' && message !== ' '){
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'email': sender_email,
                    'roomName': roomName,
                }));
                messageInputDom.value = '';
            }
        };
        
        // устанавливаем соединение
        chatSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/' +
            roomName +
            '/'
        );

        // выводим сообщение
        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            // document.querySelector('#text_area').value += (data.email + ': ' + data.message + '\n')

            
            var published_time = new Date(data.date).toLocaleString("ru", time_options);
            var message_from = '';
            if($('.chat_name_field input').val() === data.receiver){
                message_from = 'right';
            }
            else{
                message_from = 'left';
            }

            $("#text_area").append(
                '<div class="msg ' + message_from + '">'+
                    '<div class="msg_area">'+
                        '<div class="msg_text">' + data.message + '</div>'+
                        '<div class="msg_time">' + published_time + '</div>'+
                    '</div>'+
                '</div>'
                );
            $("#text_area").animate({ scrollTop: $('#text_area').prop("scrollHeight")}, 700);
        }

        document.getElementById('text_area').innerHTML = "";
    });

    // нажатие Enter отправляет запрос, а Shift+Enter добавляет новую строку
    $("#input").keypress(function (e) {
        if(e.which === 13 && !e.shiftKey) {
            e.preventDefault();
            document.querySelector('#submit').onclick();
        }
    });


    //// ----------------------------------------------------Чат на телефоне ----------------------------------------------------->
    if(( window.innerWidth <= 500 )){
        $( ".user_cover" ).click(function() {
            location.href = "#chat";
            $('.chats_container').css('display','none');
            $('.container').css('display','flex');
        });

        $(window).on('popstate', function(event) { // если возвращаемся с чата
            if(window.location.href.indexOf("#") === -1){
                $('.container').css('display','none');
                $('.chats_container').css('display','flex');
                $('.user_cover').css('background', 'initial');
                chatSocket.close();
            }
        });
    }
   

// --------------------------ПОИСК ПОЛЬЗОВАТЕЛЯ--------------------------------------- -->


    window.addEventListener("load",function(){
        if(document.getElementById('search_user')){
            document.getElementById('search_user').value = '';
        }
    });
    $(document).ready(function(){
        $("#search_user").keyup(function() {
        var search_user = $(this).val();

            
        $.ajax({
            url: '/show_chats/',
            data: {
                'search_user': search_user
            },
            success: searchSuccess,
            dataType: 'html'
        });

        });
    });


    function searchSuccess(data)
    {
        var data = JSON.parse(data);
        if(data['data'].length === 0){
            document.getElementById('chats').innerHTML = "<p style='font-weight: normal;'>Мы не смогли ничего найти( </p>";
        }
        else{
            res = data
            var arr = [];
            var a = "";
            var letter = $('#search_user').val(); // чтобы выделить букву, которую ввёл пользователь для поиска
            for (val in data['data']){ 
                email = data['data'][val]['email']
                email_input = data['data'][val]['email']


                if(data['data'][val]['first_name'] !== null && data['data'][val]['first_name'] !== '' && data['data'][val]['last_name'] !== null && data['data'][val]['last_name'] !== ''){
                    string = data['data'][val]['first_name'] + ' ' + data['data'][val]['last_name'];
                    if(string.includes(letter)){
                        email = string;
                    }
                }
                else if(data['data'][val]['first_name'] !== null && data['data'][val]['first_name'] !== ''){
                    string = data['data'][val]['first_name'];
                    if(string.includes(letter)){
                        email = string;
                    }
                }
                
                email = email.replace(letter, '<strong>'+letter+'</strong>');

                // a = '<div class="user">'+
                //         '<p>' + email + '</p>'+
                //         '<input type="hidden" value="'+email_input+'">'+
                //     '</div>';

                
                var user_image = '';


                if(data['data'][val]['image'] !== null && data['data'][val]['image'] !== ''){
                    user_image = '<div class="user_img small_img" style="background-image: url(' + data['data'][val]['image'] + ')"></div>';
                }
                else{
                    user_image = '<img src="/static/img/user_blank_'+(parseInt(Math.floor(Math.random() * 4))+1)+'.svg" class="user_img small_img" alt="">';
                }


                if($('#search_user').val() === '' || $('#search_user').val() === ' '){
                    a = '<div class="user_cover">' +
                        '<div class="user">' +
                                user_image +
                            '<div class="chat_info">'+
                                '<p>'+ email +'</p>'+
                                '<input type="hidden" value="'+email_input+'">'+
                                '<span>...</span>'
                            '</div>'+
                        '</div>'
                    '</div>';
                }
                else{
                    a = '<div class="user_cover">' +
                            '<div class="user">' +
                                    user_image +
                                '<div class="chat_info">'+
                                    '<p style="font-weight: normal; margin-bottom: 7px;">'+ email +'</p>'+
                                    '<input type="hidden" value="'+email_input+'">'+
                                '</div>'+
                            '</div>'
                        '</div>';
                }

                arr.push(a);
            }
            var data = JSON.stringify(arr);
            var counter = 0;

            data = JSON.parse(data);
            document.getElementById('chats').innerHTML = "";

            data.forEach(element => {
                document.getElementById('chats').innerHTML += element;
            });
        }
    }





// -----------------------------Загрузка сообщений чата при нажатии на пользователя------------------------------------ -->


    $(document).ready(function(){   
    
        $(document).on("click", ".user", function(e){
            // var user = $(this).attr('href');
            var user = $(this).find('input').val();

            $.ajax({
                url:"/room/",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                type:'post',
                data:{
                'user':user,
                },
                dataType:'json',
                success:function(res){
                    var _html='';
                    var days = []; // для того, чтобы писать новый день новых сообщений
                    
                    var json_data=$.parseJSON(res.posts);
                    $.each(json_data,function(index,data){
                        var options = {
                            timezone: 'UTC',
                            hour: 'numeric',
                            minute: 'numeric',
                        };
                        var day_options = {
                            month: 'long',
                            day: 'numeric',
                            timezone: 'UTC',
                        };
                        var published_time = new Date(data.fields.date).toLocaleString("ru", options);
                        var published_day = new Date(data.fields.date).toLocaleString("ru", day_options);
                        var day = '';

                        if(!days.includes(published_day)){
                            days.push(published_day);
                            day = '<div class="day">' + published_day + '</div>';
                        }

                        var receiver = user;
                        var sender = '';
                        var message_from = '';

                        if(receiver === data.fields.receiver){
                            message_from = 'right';
                        }
                        else{
                            message_from = 'left';
                        }

                        _html+= day +
                        '<div class="msg ' + message_from + '">'+
                            '<div class="msg_area">'+
                                '<div class="msg_text">' + data.fields.value + '</div>'+
                                '<div class="msg_time">' + published_time + '</div>'+
                            '</div>'+
                        '</div>';
                    });
                    $("#text_area").append(_html);

                    // прокручиваем блок вниз, чтобы увидеть сообщение
                    $("#text_area").animate({ scrollTop: $('#text_area').prop("scrollHeight")}, 0);
                }
            });
        });
    
    });
