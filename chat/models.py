from django.db import models
from datetime import datetime
from django.core.files.base import ContentFile, File
import uuid
from PIL import ExifTags, Image as PIL_Image
from pytils.third.six import BytesIO
import os


class Room(models.Model):
    name = models.CharField(max_length = 500, verbose_name='Чат')
    # participants = models.ManyToManyField('account.Account', related_name="participants", default=None, blank=True, verbose_name = "Участники чата")
    participant_1 = models.ForeignKey('account.Account', on_delete=models.CASCADE, verbose_name='Участник 1', related_name='participant_1', blank=True, null=True)
    participant_2 = models.ForeignKey('account.Account', on_delete=models.CASCADE, verbose_name='Участник 2', related_name='participant_2', blank=True, null=True)

    
    def __str__(self):
        return self.name

class Message(models.Model):
    value = models.CharField(max_length = 10000, verbose_name='Сообщение')
    room = models.ForeignKey('Room', on_delete=models.CASCADE, verbose_name='Чат №')
    date = models.DateTimeField(default = datetime.now, blank = True, verbose_name='Дата отправки')
    sender = models.CharField(max_length = 10000, verbose_name='Отправитель', blank=True)
    receiver = models.CharField(max_length = 10000, verbose_name='Получатель', blank=True)


    # class Meta:
    #     get_latest_by = 'id' # Это нам нужно для того, чтобы мы могли получить последний опубликованный объект в views.py через .latest()






def translate(string):
    dic = {'Ь':'', 'ь':'', 'Ъ':'', 'ъ':'', 'А':'A', 'а':'a', 'Б':'B', 'б':'b', 'В':'V', 'в':'v',
        'Г':'G', 'г':'g', 'Д':'D', 'д':'d', 'Е':'E', 'е':'e', 'Ё':'E', 'ё':'e', 'Ж':'Zh', 'ж':'zh',
        'З':'Z', 'з':'z', 'И':'I', 'и':'i', 'Й':'I', 'й':'i', 'К':'K', 'к':'k', 'Л':'L', 'л':'l',
        'М':'M', 'м':'m', 'Н':'N', 'н':'n', 'О':'O', 'о':'o', 'П':'P', 'п':'p', 'Р':'R', 'р':'r', 
        'С':'S', 'с':'s', 'Т':'T', 'т':'t', 'У':'U', 'у':'u', 'Ф':'F', 'ф':'f', 'Х':'Kh', 'х':'kh',
        'Ц':'Tc', 'ц':'tc', 'Ч':'Ch', 'ч':'ch', 'Ш':'Sh', 'ш':'sh', 'Щ':'Shch', 'щ':'shch', 'Ы':'Y',
        'ы':'y', 'Э':'E', 'э':'e', 'Ю':'Iu', 'ю':'iu', 'Я':'Ia', 'я':'ia'}
        
    alphabet = ['Ь', 'ь', 'Ъ', 'ъ', 'А', 'а', 'Б', 'б', 'В', 'в', 'Г', 'г', 'Д', 'д', 'Е', 'е', 'Ё', 'ё',
                'Ж', 'ж', 'З', 'з', 'И', 'и', 'Й', 'й', 'К', 'к', 'Л', 'л', 'М', 'м', 'Н', 'н', 'О', 'о',
                'П', 'п', 'Р', 'р', 'С', 'с', 'Т', 'т', 'У', 'у', 'Ф', 'ф', 'Х', 'х', 'Ц', 'ц', 'Ч', 'ч',
                'Ш', 'ш', 'Щ', 'щ', 'Ы', 'ы', 'Э', 'э', 'Ю', 'ю', 'Я', 'я']
    

    st = string
    result = str()
    
    len_st = len(st)
    for i in range(0,len_st):
        if st[i] in alphabet:
            simb = dic[st[i]]
        else:
            simb = st[i]
        result = result + simb

    return result.replace(' ','_').lower()

class File(models.Model):
    file = models.FileField()
    this_name = models.CharField(max_length = 10000, verbose_name='Имя файла', blank=True)
    user = models.ForeignKey('account.Account',null=True, blank=True, on_delete=models.CASCADE,verbose_name='Пользователь')  
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self._state.adding: # У ModelStateобъекта есть два атрибута: addingфлаг , указывающий, Trueчто модель еще не была сохранена в базе данных, и db строка, относящаяся к псевдониму базы данных, из которого был загружен или сохранен экземпляр.

            filename = translate(self.file.name[:self.file.name.rfind('.')])
            file_format = self.file.name[self.file.name.rfind('.')+1:]
            self.this_name = self.file.name

            try:
                image = PIL_Image.open(self.file) 
                filename = filename + '.jpg'

                try:
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                except:
                    pass

                try:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    exif = dict(image._getexif().items())

                    if exif[orientation] == 3:
                        image = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image = image.rotate(90, expand=True)
                except:
                    pass

                image_io = BytesIO()
                image.save(image_io, format='JPEG', quality=70)

                # change the image field value to be the newly modified image value
                self.file.save(f'uploaded_files/images/{datetime.today()}__{str(uuid.uuid4())}.jpg', ContentFile(image_io.getvalue()), save=False)
            except:
                self.file.save('uploaded_files/files/' + filename + f'{str(uuid.uuid4())}.' + file_format, self.file, save = False)

            super(File, self).save(*args, **kwargs)
        else:
            super(File, self).save(*args, **kwargs)
            
        # os.remove(f'images/{filename}')