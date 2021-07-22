from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from .models import ACL
from ownerlist.models import Owners, Iplist
import os
from ownerlist.utils import make_doc, MakeMarkDown, request_handler, is_valid_uuid, ip_status, logger, get_client_ip, MakeTemporaryToken
from ownerlist.utils import FORM_APPLICATION_KEYS, FORM_URLS, BaseView, GitWorker, BASE_DIR, UpdateCallBackStatus, ClearSessionMeta
import json
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
import re
import sys
from django.contrib.auth.models import User, Group
from .forms import Approve_form
from django.db.models import Q
from django.core.mail import EmailMessage, send_mail

class ObjectMixin:
    """Миксин обработки запросов и отобращение страниц"""
    template = None
    url = None

    def get(self, request, acl_id=None):
        if acl_id is None:
            if 'uuid' in request.session is not None:
                if request.session['uuid']:
                    return redirect(reverse(self.url, kwargs={'acl_id': request.session['uuid']}))

            if 'HTTP_REFERER' in request.META.keys():
                if reverse(FORM_URLS[0]) in request.META.get('HTTP_REFERER'):
                    # Заполняем uuid для нового acl
                    request.session['uuid'] = str(uuid.uuid4())
                    request.session['LOCAL_STORAGE'] = {}
                    request.session['taskid'] = None
                    return HttpResponseRedirect(reverse(FORM_URLS[1], kwargs={'acl_id': request.session['uuid']}))
        else:
            if 'uuid' in request.session is not None:
                  if '/new/' in request.path:
                      if str(acl_id) != request.session['uuid']:
                         return HttpResponseRedirect(reverse(FORM_URLS[0]))
                  elif str(acl_id) == request.session['uuid']:
                     return redirect(reverse(self.url, kwargs={'acl_id': request.session['uuid']}))
            context = {}
            if '/new/' not in request.path:
                tmp = get_object_or_404(ACL, id=str(acl_id))
                request.session['LOCAL_STORAGE'] = json.loads(tmp.acltext)
                request.session['taskid'] = tmp.taskid or ''

                if tmp.status in ['WTE', 'APRV', 'CNL']:
                    if tmp.owner == request.user or request.user.is_staff:
                        context.update({'acl_owner': tmp.owner})
                    else:
                        response = HttpResponseRedirect(reverse('acl_pending_urls', kwargs=({'acl_id': acl_id})))
                        response['Location'] += "?token={}".format(tmp.token)
                        return response

                    if tmp.approve == request.user:
                        context.update({'debtor': 'True',
                                        'token': tmp.token})

                    context.update({'status': str(tmp.status),
                                    'app_person': tmp.approve})

            context.update({'acl_id': str(acl_id),
                       'FULL_STORAGE': request.session['LOCAL_STORAGE'],
                       'FORM_APPLICATION_KEYS': FORM_APPLICATION_KEYS,
                       'template_name': self.template,
                       })

            if 'LOCAL_STORAGE' in request.session:
                if self.template not in request.session['LOCAL_STORAGE']:
                    return render(request, self.template, context=context)
                else:
                    context['LOCAL_STORAGE'] = request.session['LOCAL_STORAGE'][self.template]
                    return render(request, self.template, context=context)

        return HttpResponseRedirect(reverse(FORM_URLS[0]))

    def post(self, request, acl_id=None):
        if acl_id is not None:
            tmp = request_handler(request, self.template)
            current_page = FORM_URLS.index(self.url)
            if tmp:
                try:
                    if len(tmp[self.template]) == 0 or len(tmp[self.template][0]) == 0 or len(tmp[self.template][0][0]) == 0:
                        if self.template in request.session['LOCAL_STORAGE']:
                            del request.session['LOCAL_STORAGE'][self.template]
                    else:

                        if self.template in request.session['LOCAL_STORAGE']:
                            request.session['LOCAL_STORAGE'].update({self.template: tmp[self.template]})
                        else:
                            request.session['LOCAL_STORAGE'][self.template] = tmp[self.template]
                except:
                    request.session['LOCAL_STORAGE'][self.template] = tmp[self.template]

                request.session.modified = True

                if '/new/' in request.path:
                    if 'uuid' not in request.session or request.session['uuid'] != str(acl_id):
                        logger.warning('Попытка записи в чужой uuid')
                        return redirect(reverse(FORM_URLS[current_page + 1], kwargs={'acl_id': acl_id}))
                    #else:
                    #    return HttpResponseRedirect(reverse(FORM_URLS[0]))
                if FORM_APPLICATION_KEYS[0] in request.session['LOCAL_STORAGE']:
                        owner_form = request.session['LOCAL_STORAGE'][FORM_APPLICATION_KEYS[0]]
                else:
                    messages.warning(request, 'Для продолжения, необходимо заполнить контактные данные.')
                    return redirect("{}{}/".format(reverse(FORM_URLS[1]), acl_id))
                save__form(request, owner_form, acl_id)
                return redirect("{}{}/".format(reverse(FORM_URLS[current_page + 1]), acl_id))

        messages.warning(request, 'Не все поля заполнены')
        return render(request, self.template, context={'acl_id': acl_id})



class Aclhistory(BaseView, LoginRequiredMixin, View):
    """История запросов"""
    def get(self, request, acl_id=None):
            ClearSessionMeta(request)
            if acl_id is not None:
                if request.user.is_staff:
                    acllist= ACL.objects.filter(id__exact=acl_id)
                else:
                    acllist = ACL.objects.filter(id__exact=acl_id, owner__email__iexact=request.user.email)
            else:
                if request.user.is_staff:
                    acllist = ACL.objects.order_by("-created", "-pkid")
                else:
                    acllist = ACL.objects.filter(Q(owner_id=request.user.id) | Q(approve__exact=request.user)).order_by("-created", "-pkid") #owner__email__iexact=request.user.email

            paginator = Paginator(acllist, 10)
            page_number = request.GET.get('page', 1)
            page = paginator.get_page(page_number)

            is_paginated = page.has_other_pages()

            if page.has_previous():
                prev_url = '?page={}'.format(page.previous_page_number())
            else:
                prev_url = ''

            if page.has_next():
                next_url = '?page={}'.format(page.next_page_number())
            else:
                next_url = ''

            context = {
                "acl": ACL,
                "acllists": page,
                "is_paginated": is_paginated,
                "next_url": next_url,
                "prev_url": prev_url
            }

            return render(request, 'acl_history.html', context=context)


class AclCreate(BaseView, ObjectMixin, View):
    template = 'acl_create_info.html'
    url = 'aclcreate_urls'


class AclCreate_internal(BaseView, ObjectMixin, View):
    template = 'acl_internal_resources.html'
    url = 'aclinternal_urls'


class AclCreate_dmz(BaseView, ObjectMixin, View):
    template = 'acl_dmz_resources.html'
    url = 'acldmz_urls'


class AclCreate_external(BaseView, ObjectMixin, View):
    template = 'acl_external_resources.html'
    url = 'aclexternal_urls'


class AclCreate_traffic(ObjectMixin, View):
    template = 'acl_traffic.html'
    url = 'acltraffic_urls'


class Acl_approve(View):
    """Функция для страницы согласования"""
    def get(self, request, acl_id=None):
        context = {}
        if acl_id is None:
            messages.warning(request, 'Неправильный запрос')
            return redirect(reverse('acldemo_urls'))

        tmp = get_object_or_404(ACL, id=str(acl_id))

        if tmp.status == 'WTE':
            #messages.warning(request, 'ACL уже ожидает согласование')
            return redirect(reverse('acl_pending_urls', kwargs=({'acl_id': acl_id})))

        form = Approve_form()
        APPROVE_OWNER = User.objects.filter(groups__name=settings.APPROVE).filter(groups__name=tmp.project)
        if APPROVE_OWNER:
            # Берем только одного человека для согласования

            APPROVE_OWNER = APPROVE_OWNER[0]
            APPROVE_LIST = User.objects.filter(groups__name=settings.APPROVE).exclude(id__exact=APPROVE_OWNER.id)
        else:
            APPROVE_LIST = User.objects.filter(groups__name=settings.APPROVE)

        context.update({'acl_id': str(acl_id),
                        'FULL_STORAGE': request.session['LOCAL_STORAGE'],
                        'FORM_APPLICATION_KEYS': FORM_APPLICATION_KEYS,
                        'APPROVE_LIST': APPROVE_LIST,
                        'APPROVE_OWNER': APPROVE_OWNER,
                        'PROJECT': tmp.project,
                        'STATUS': tmp.status,
                        'REASON': tmp.taskid,
                        'form': form,
                        })


        return render(request, 'acl_approve.html', context=context)


    def post(self, request, acl_id=None):
        form = Approve_form(data=request.POST or None)
        if form.is_valid():
            tmp = get_object_or_404(ACL, id=str(acl_id))
            if tmp.token == '':
                tmp.token = MakeTemporaryToken()
            user = form.cleaned_data['approve_person']
            if not user:
                messages.error(request, 'К сожалению, возникли проблемы с данным пользователям')
            else:
                user_obj = None
                try:
                    user_obj = User.objects.get(username__exact=user) or None
                    if not user_obj.groups.filter(name=settings.APPROVE):
                        user_obj = None
                except User.DoesNotExist:
                    messages.error(request, 'Выбранный пользователь не может согласовать данный ACL')

                if user_obj:
                        EMAIL_APPROVE = '''
                        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><meta charset="utf-8"><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>Согласование обращения</title><style>.container{margin: 0 auto;padding: 10px; width: 600px;height: 200px;border-left: 3px solid #6a68d9;border-right: 1px solid #ccc;border-top: 1px solid #ccc;border-bottom: 1px solid #ccc;}.header{border-bottom: 1px solid #ccc;padding: 5px;margin: 15px;display: flex;}.header_text{color: #6a68d9;padding-right: 40px;display: inline;}.header_text_portal{ color: #484848; font-weight: bold;}.logo{display: block; float: left;}.container_body{margin: 15px;min-height: 165px;}.container_footer{display: flex;align-items: center;}.footer{color: #48484859;padding: 15px;border-top: 1px solid #ccc;max-height: 57px;}</style></head><body> <div class="container"><table cellpadding="0" cellspacing="0" border="0"> <tr style="border-bottom: 1px solid #ccc;"> <td style="padding-right: 15px"><img src="data:image/png;base64,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" class="logo"></td><td style="padding-right: 15px"><h4 class="header_text">Cогласование</h4></td><td><div class="header_text_portal" style="padding-top: 10px"><h3 style="margin-left: 15px; color: #484848cc;">ACL Портал</h3></div></td> </tr> <tr style="padding-top: 10px"> <td colspan="3" style="">Ожидается ваше согласование</td> </tr> <tr style="padding-top: 10px"> <td colspan="2" style="padding-top: 10px">Запрос от:</td> <td style="font-weight: bold;">%s</td> </tr><tr style="padding-top: 10px"><td colspan="2">Подробнее:</td> <td><a href="%s" style="color:#1a73e8;">Перейти на портал</a></td> </tr></table><div class="footer"><p>Данное сообщение сформировано автоматически порталом acl.vesta.ru, просьба не отвечать на него.</p><div> </div></body></html>
                        ''' % (tmp.owner, "https://acl.vesta.ru/acl/pending/{}/?token={}".format(acl_id, tmp.token))
                        tmp.status = 'WTE'
                        tmp.approve = user_obj
                        tmp.save()
                        e = EmailMessage(subject='Согласование обращения', body=EMAIL_APPROVE, from_email='acl@alfastrah.ru',
                                         to=[user_obj.email])
                        e.content_subtype = "html"
                        e.send(fail_silently=settings.DEBUG)
                        response = redirect(reverse('acl_pending_urls', kwargs=({"acl_id": acl_id})))
                        #response['Location'] += "?token={}".format(tmp.token)
                        return response
        if not messages.get_messages(request):
            messages.error(request, 'Произошла ошибка при изменении данных, вероятно невалидные данные в форме: {}'.format(form.errors))
        return HttpResponseRedirect(reverse('acl_approve_urls', kwargs=({"acl_id": acl_id})))


class Acl_pending(View):
    """Функция вывода информации об согласовании объекта"""
    def get(self, request, acl_id=None):
        if acl_id is None:
            return redirect(reverse(FORM_URLS[1]))
        token = request.GET.get('token', '')
        context = {}
        tmp = get_object_or_404(ACL, id=str(acl_id))


        if token != tmp.token:
            context.update({'IS_APPROVE': False})
            if not request.user or request.user != tmp.owner:
                messages.warning(request, 'Вы не можете долучить доступ к данному ACL')
                return redirect(reverse('acldemo_urls'))
        else:
            context.update({'IS_APPROVE': True})
            #messages.warning(request, 'Не валидный токен, попробуйте запросить новый')
            #return redirect(reverse(FORM_URLS[1]))
        if tmp.status == 'APRV':
            return redirect(reverse('acloverview_urls', kwargs={'acl_id': acl_id}))

        if tmp.status != 'WTE':
            messages.warning(request, 'ACL вероятно уже согласован, либо редактируется кем-то другим')
            return redirect(reverse('acl_approve_urls', kwargs={'acl_id': acl_id}))

        context.update({'status': str(tmp.status)})
        context.update({'acl_id': str(acl_id), 'LOCAL_STORAGE': json.loads(tmp.acltext)})
        context.update({'APP_PERSON': tmp.approve})
        context.update({'OWNER': tmp.owner})
        return render(request, 'acl_pending.html', context=context)

class AclDemo(BaseView, View):
    """Страница приветствия"""
    def get(self, request):
        ClearSessionMeta(request)
        return render(request, 'acl_demo.html')


def ACldefault(request):
    request.session.set_expiry(0)
    return HttpResponseRedirect(reverse('acldemo_urls'))


def save__form(request, owner_form:None, acl_id)->None:
    """Сохранение данныех из сесии в БД"""
    if owner_form[1] != request.user.email:
        email = request.user.email
    else:
        email = owner_form[1]
    user, created = Owners.objects.get_or_create(email=email)
    if created:
        user.username = owner_form[0]
        user.phone = owner_form[2]
        user.active = True
        user.department = owner_form[3]
        user.save()
    try:
        ip, created_ip = Iplist.objects.get_or_create(ipv4=get_client_ip(request))

        ip.owner = user
        ip.save()

        obj, created = ACL.objects.get_or_create(id=str(acl_id))
        if obj:
            obj.acltext = json.dumps(request.session['LOCAL_STORAGE'])
            obj.is_executed = False
            # Не перезаписывать владельца ACL
            if created:
                obj.owner = request.user

            if len(request.session['LOCAL_STORAGE']) <= 1:
                  obj.status = 'NOTFL'
            else:
                if not created and obj.status == 'NOTFL':
                    obj.status = 'FL'

            obj.project = owner_form[4]
            obj.save()

    except Exception as e:
        messages.error(request, 'Ошибка, мы не смогли записать данные в БД. {}'.format(e))
    finally:
        return obj or None

class AclOver(BaseView, LoginRequiredMixin, View):
    """Страница формирования ACL файла и других активностей"""
    def get(self, request, acl_id=None):
        if acl_id is None or 'LOCAL_STORAGE' not in request.session: # or 'uuid' not in request.session
            return HttpResponseRedirect(reverse('acldemo_urls'))

        context = {'obj': acl_id,
                   'file_download': None,
                   'file_md': None,
                   'gitproc': None
                   }
        if 'uuid' in request.session is not None:
                    if '/new/' in request.path:
                        if str(acl_id) != request.session['uuid']:
                            return HttpResponseRedirect(reverse(FORM_URLS[0]))
                    elif str(acl_id) == request.session['uuid']:
                        return redirect(reverse('acloverview_urls', kwargs={'acl_id': acl_id}))

        tmp = get_object_or_404(ACL, id=str(acl_id))

        """Проверяем состояние массива с данными"""
        # and all(KEY in request.session['LOCAL_STORAGE'] for KEY in FORM_APPLICATION_KEYS):

        if len(request.session['LOCAL_STORAGE']) > 1: #or tmp.status == 'NOTFL'
            owner_form = request.session['LOCAL_STORAGE'][FORM_APPLICATION_KEYS[0]]
            obj = save__form(request, owner_form, acl_id)
        else:
            messages.warning(request, 'Нехватает данных для формирования ACL')
            return redirect(reverse(FORM_URLS[1], kwargs={'acl_id': acl_id}))



        #Требовать согласование при формировании обращения
        if 'ACT_MAKE_GIT' in request.session:

            if tmp.status in ['FL', 'CNL']:
                t = reverse('acl_approve_urls', kwargs={'acl_id': acl_id})
                return HttpResponseRedirect(t)

            if tmp.status != 'APRV':
                messages.warning(request, 'Данный ACL не получил согласования')
                return HttpResponseRedirect(reverse('aclcreate_urls', kwargs={'acl_id': acl_id}))

            context['gitproc'] = True


        if 'ACT_MAKE_DOCX' in request.session:
                context['file_download'] = True
        #if 'ACT_MAKE_GIT' in request.session:



        return render(request, 'acl_overview.html', context=context)


@csrf_exempt
def AclStageChange(request,  *args, **kwargs):
    if request.method == 'POST':
        result = {'status': 'Статус изменен'}

        uuid = request.POST.get('uuid', '')
        text = request.POST.get('text', '')
        stage = request.POST.get('stage', '')
        if stage not in ['NOTFL', 'FL', 'CMP', 'WTE', 'APRV', 'CNL']:
            result = {'error': 'Ошибка данных'}
        else:
            if stage == 'WTE':
                result = {'error': 'Нельзя изменить статус на данный тип'}
            else:
                if (uuid!= '' and is_valid_uuid(uuid) and stage!=''):
                        try:
                            if text == '' and stage == 'CNL':
                                text = "Отклонено согласующим без указании причины"
                            acl = ACL.objects.get(id=uuid)
                            if acl:
                               acl.status = stage
                               acl.taskid = text
                               acl.token = MakeTemporaryToken()
                               acl.approve = None
                               acl.save()

                        except ACL.DoesNotExist:
                            result = {'error': 'Ошибка, таких данных нет'}
                        if stage in ['APRV', 'CNL']:
                                EMAIL_APPROVE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><meta charset="utf-8"><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>Согласование обращения</title><style>.container{margin: 0 auto;padding: 10px; width: 600px;height: 200px;border-left: 3px solid #6a68d9;border-right: 1px solid #ccc;border-top: 1px solid #ccc;border-bottom: 1px solid #ccc;}.header{border-bottom: 1px solid #ccc;padding: 5px;margin: 15px;display: flex;}.header_text{color: #6a68d9;padding-right: 40px;display: inline;}.header_text_portal{ color: #484848; font-weight: bold;}.logo{display: block; float: left;}.container_body{margin: 15px;min-height: 165px;}.container_footer{display: flex;align-items: center;}.footer{color: #48484859;padding: 15px;border-top: 1px solid #ccc;max-height: 57px;}</style></head><body> <div class="container"><table cellpadding="0" cellspacing="0" border="0"> <tr style="border-bottom: 1px solid #ccc;"> <td style="padding-right: 15px"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACIAAAAdCAYAAADPa766AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAjmSURBVFhHnZf5cxTXEcf5P/NLChNwQAJZIAQ6AxEORcrEFQgkwcE2ijGC4IAx6OQQh2PMoZtokdBKitCFrtXu7Nz7zaffSjIkdlUqszQz86bf6+/r/na/1jYlkkkaS3FsLysqKa+UX5LwXtqUFKUSgsr/IzbfSUlxyFAJO6WCSnFJJd63/aCMkVLMzUCE3EtKGU9BmKa8pxGS/IfYN5OfekcwXn62+aESnlkaG6vc15VEEY5IAeJQ4A6hCDSHB/F9qZC3L+yAb/8t4f8gEc6Ot6Q8L1UR22kpYGUPW0X2XzAgjIrBkqc4AYgBRPwiX3BZCMaQ94D7ptiYeyZi77xviJvzE+8RUgycExTxUir5RMwBsT0buiIowV0oaXQ41Nk/dKu66jPt3XMT6UI6kXbtrbilShurKEvlnlvc21W5275tio3Zt29UsZu7fWONqsoeVe1r1/Wvs8qtpoqdZyLABAYEsuC4FM+kkOLJ/aKaajv1+acP1d05op6uLDKpbpPurJPOjgl1dmZ1796MOtondKdnWh23Xjm9nu6ybo/TnSjP4b2rYxJd5NaEjh+/r1MfTWtpHs9AgySJtY07QGyACMaxzpzI6XLrkvLww9wYohlCnGBDQgjEHtzdCWPFgDFcbaEKzeWmY99MD9l6N2G9V9lEVb8c0IO7oSLmRDFkNRBG14SwRKRv1fZhjfQVt2KaMBmeI0Y8WC8ffRawDLBvBg7rlmEWd9th6vSNoIHTT0gC26izgX4O/h2tn9BXbbMie908gCTuF6McwdLqHS81OuiDPlUhzLtakgIwgchJyqIJ5OIZW+WyQJxjP9HYiyWFHoB4D4ukPhaSxJLAdBl0tYh/SAEwdbUDunQxK59aEvMNIJZQpBbsDWBP9c4JDfX5LtGCdI2JBtniZwsZuwAVmSEeeQWXvJVQ9ftb9aB7TrHHOLbNzSU2UHJuQsxlrAUGFdhccyNALo3zvIxtOOLiYkUHF4aQpvK9ab0YDlwuuepK/KwgRVgIYkNPKJjjAeT1m1RTMwU9f17QgaoJ7fr5oHrvLMMZ88S6SgFsAiiRxARrpoQcJD5gmuv6dfnSFNzZCI3bLR8t7gFIK9/71xYQF2m8FDMes6MIQEVQzM5JF/86p6ampzp46IH2f5DR9p+9Vs3egpoanqBnxM+xLusEEMIIGXmuiPnUdx/DzXWDugIQ44g5awOI/YNaQKvckdWLEd+CBRCrtjE7zAEEEKz56P4bVb3frd+2ZHT96ooms9L0y1Q1e+Z1aN+4MhkfsLif8mnHRETsghBe8RzHEB0wgQPSD5DJt4DgYgNjTA+gfOUvxgBSZLicfAG+K8QzZFFR7dfmVV81oEe3lylIzGGRfCGQtxTrQxbODEXKA6DImlY9B4aKml8k5HAlZe0U75Yg0BaQtmwZCFIGYsTjxRQqd44ABC7wM96Yl0LOg/6+vGr3PNe9b1YVEfcYtydpDrDo4uvVRauUuJ1T1c6S3t68du/p0anfv9TKCus7ruNlNmYcKwOZAIgdjKWN0JhHAOLh0n3vD2jEAYEhVuRQKsKuj44/Vuu5ZXmE3roDS+mUhVMDxMoRKZw4Qib6/qmnquoeXWgtqA4u3Li2KI+jw1ItBYgH0CONI2r7clxeUm45toAkBKpoZN31mN2vu4JmbPa5Z8elw9X3NDnOiQrikAochQDlbkD8ArDRi+DQwDNfhw8+UtuVaS2vS385P6qWpn7lbQNWh8wOuo21Q2TNK4CsOe+W09d5BI6Qxru239XI8LojptUKi/W1v3k60TKi/DogiLVlRZgUmJMjpddc0YvRywwkaql7pc8/WYArFERAD42uqv7AsGZnCbFlE3bWqDVH68cAkuUdj5DjACmzxcqvRx050jCi3tt5+SiHgLF4nmh5qc/+OCcfY+tFX88GXyjv5+EUpGZ6gazIZIqqqxnU+T9NyTKWEsL+Ii2t5VS966my2VDrKK+xxsJyqsP7M+psh28AiWlBNoC40sXJEOvKl2uqO/idnvwj71xNUujD5nGdOzNVLmILsT6ouKu2L+bdWbSyJq3lqJTN3+vMWcLBc0TJjdlBQB7H1I36vRmABsqhP4/+hS9eqqFmWmMZOwyxA0+2Wdl1ldWICdHWlku6emlMRxvb1HT4M+fSc6eW9efTWUcyi2/fU6nhAGRrXdE/h1K1NGd0+uSAchgJMZzSeQVwCApp5rV0oKJf09lYt7rmVV1zUb/7+IaePcabJEdCWKyYloHwWAJMbGeI8YX72lIkbz2gIpbU8bWvloYBrS5T3FDwmfP4u4IO7hvFSAbQo1qcJobUiZR2zicuVgqslP/9xpSOND/R8gLZkkupP6FyOWsR4VtIrXL2LX35z3Vpls/GFXZh55sdaL4fUUNWtLiQqvngcz3soU4Q54ATM8d50t0zo7NnRvSGOmHtZQJBXVm36omBhdVYvzlxR+c+eeaqbZgU8cCSO8kNwKbEuO4HIK7dKXfYBsayyZ7ZAxNT3by6qMbqjKZIZfogGssVK3f8IHDqMdM2Y1wrUIk9F8Leh8vaf+C6JqbtkLR+htNci86eXdYRBmzI7m95xFpFQ2p/zwDJvAKYiAV8wrM4l+pYQ7/OnMxqDt7Ywh4APEAWiXMRl1ij5NGq5QrSg0cF1dZ2q6NrhkPOjg/aCrIrsfAxx4yXw2Ibfis0mISwuNUaH7BvKvqhtU3lehJa/jd8q/0VXep7EssjqzzK/TrjFFaM8UyLeeVyXjt3dNBvTLuQ5Kj51snZQtQ011DZ5eqPMZprA4iZsoG3xcYAZ6Ghy7KDy3Y8Oxvpq8uT+hUd1q/rRvXpuTFdvPBCra19On16QIdrnpPur/T4W18e4COyEYpjhTUNgC1bdsQ71wYQ0/gxsZDRrUFQq7wxh591U5Z2q29oCXpDfXzythoP3dSxY906f35Qw1TXiHQJmZMr5liFg9G1iyznQmGbtLXfvQCyeTnNd4WJlg2uS8S19geYHWpWyOweUhFDeGWduFVdmjlAEyLSMko8ZIlV7KxgLfOE3X/UJdK/AfklVKxVmjCRAAAAAElFTkSuQmCC" class="logo"></td><td style="padding-right: 15px"><h4 class="header_text">Cогласование</h4></td><td><div class="header_text_portal" style="padding-top: 10px"><h3 style="margin-left: 15px; color: #484848cc;">ACL Портал</h3></div></td> </tr> <tr style="padding-top: 10px"> <td colspan="3" style="">Статус Вашего запроса ACL изменён.</td> </tr><tr style="padding-top: 10px"><td colspan="2">Подробнее:</td> <td><a href="https://acl.vesta.ru/acl/approve/%s/" style="color:#1a73e8;">Перейти на портал</a></td> </tr></table><div class="footer"><p>Данное сообщение сформировано автоматически порталом acl.vesta.ru, просьба не отвечать на него.</p><div> </div></body></html>""" %(uuid)
                                e = EmailMessage(subject='Статус обращения', body=EMAIL_APPROVE, from_email='acl@alfastrah.ru',
                                                 to=[acl.owner.email])
                                e.content_subtype = "html"
                                e.send(fail_silently=settings.DEBUG)
                        elif stage == 'WTE':
                            pass
                else:
                    result = {'error': 'Ошибка данных'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)

@csrf_exempt
def Gitcheck(request):
    """Функция сохранения и проверки git проекта"""
    if request.method == 'POST':
        result = {'status': 'Данные сохранены'}
        if 'git_url' in request.POST:
                if request.POST.get('git_url', '') == '':
                    if 'GIT_URL' in request.session:
                        del request.session['GIT_URL']
                    result = {'error': 'Git проект не может быть пустым'}
                elif not re.match('^(https:\/\/git)?(.)+(.git)$',request.POST.get('git_url', '')):
                   result = {'error': 'Не валидные данные'}
                else:
                    request.session['GIT_URL'] = request.POST.get('git_url')

        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)


def CheckIp(request, ip=None):
    """Функция возвращает данные по IP"""
    return HttpResponse(json.dumps(ip_status(ip)), content_type="application/json")

@csrf_exempt
def AclRemove(request, *args, **kwargs):
    """Функция удалеяет данные по uuid"""
    if request.method == 'POST':
        result = {'error': 'Ошибка при удалении acl'}
        if 'uuid' in request.POST:
                if is_valid_uuid(request.POST.get('uuid', 0)):
                       try:
                            obj = ACL.objects.get(id=request.POST.get('uuid'))
                            if obj:
                                obj.delete()
                                result = {'status': 'Запись acl удалена'}
                       except ACL.DoesNotExist:
                            result = {'error': 'Не всё записи удалены'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)


@csrf_exempt
def OverViewStatus(request)->bool:
    """Функция обработки запросов на выполнение активностей для выполнения обращения"""

    result = {}
    if 'uuid' not in request.POST or not is_valid_uuid(request.POST['uuid']) or not 'LOCAL_STORAGE' in request.session:
        result = {'status': 'error'}
        return HttpResponse(json.dumps(result), content_type="application/json")

    uid = request.POST['uuid']
    JOB = cache.get(uid, {})

    if JOB == {}:
        if 'ACT_MAKE_DOCX' in request.session or 'ACT_MAKE_GIT' in request.session:
            cache.set(uid, {}) #create cache for job activity
        else:
            return HttpResponse(json.dumps({'status': 'complete'}), content_type="application/json")

    else:
        if 'ACT_MAKE_DOCX' in request.session or 'ACT_MAKE_GIT' in request.session:
            return HttpResponse(json.dumps({'status': JOB}), content_type="application/json")
        else:
            cache.delete(uid)
            return HttpResponse(json.dumps({'status': JOB}), content_type="application/json")

    if 'ACT_MAKE_DOCX' in request.session:
                    UpdateCallBackStatus(uid, 'docx_download_status', 'Генерация docx файла')
                    try:
                        result = make_doc(request, request.session['LOCAL_STORAGE'], uid)
                    except Exception as e:
                        UpdateCallBackStatus(uid, 'docx_download_status', 'Произошла ошибка при создании docx файла: {}'.format(e), 0)
                    finally:
                        del request.session['ACT_MAKE_DOCX']
                        if result:
                            UpdateCallBackStatus(uid, 'docx_download_status', result)


    if 'ACT_MAKE_GIT' in request.session:
                    UpdateCallBackStatus(uid, 'git_upload_status', 'Генерация md файла')
                    try:
                        file_md = MakeMarkDown(request, request.session['LOCAL_STORAGE'], 'acl_{}'.format(uid), uid) or 'None'
                        if not file_md:
                            raise Exception('Ошибка при создании md файла')

                        UpdateCallBackStatus(uid, 'git_upload_file', file_md)
                        file_md_abs = os.path.join(BASE_DIR, 'static/md/' + 'acl_{}'.format(str(uid)) + '.md')
                        if '/' in file_md_abs:
                            if 'linux' not in sys.platform:
                                    file_md_abs = file_md_abs.replace('/', '\\')
                        if not os.path.exists(file_md_abs):
                                file_md_abs = os.path.join(BASE_DIR, 'static/md/' + 'acl_{}'.format(str(uid)) + '.md')
                                UpdateCallBackStatus(uid, 'git_upload_status', 'Ошибка при формировании пути md файла', 0)
                                return HttpResponse(json.dumps({'status': cache.get(uid, {})}), content_type="application/json")
                        if 'GIT_URL' not in request.session:
                            raise Exception('Неправильный url для git репозитория {}'.format(request.session['GIT_URL']))

                        if 'GIT_USERNAME' not in request.session or 'GIT_PASSWORD' not in request.session:
                            raise Exception('Невалидные учетные данные для аутентификации')
                        UpdateCallBackStatus(uid, 'git_upload_status', 'Отправка запроса в gitlab')
                        g = GitWorker(request, request.session['GIT_URL'], request.session['GIT_USERNAME'],
                                                request.session['GIT_PASSWORD'], None, file_md_abs, taskid=uid)
                        if g:
                                      if g.clone():
                                          f = g.activity()
                                          if f:
                                              if g.addindex(f):
                                                  UpdateCallBackStatus(uid, 'git_upload_status',
                                                                       "Отправка изменений на сервер")
                                                  if g.push():
                                                      UpdateCallBackStatus(uid, 'git_upload_status',
                                                                           "Файл acl.md успешно загружен в репозиторий")
                                                      if settings.DEBUG:
                                                          logger.debug('Файл загружен в проект')
                                      g.free()
                    except Exception as e:
                        UpdateCallBackStatus(uid, 'git_upload_status', '{}'.format(e), 0)
                    finally:
                                  del request.session['ACT_MAKE_GIT']
                                  del request.session['GIT_URL']
                                  if settings.DEBUG:
                                      logger.debug('Очистка переменных GIT')

    return HttpResponse(json.dumps({'status': cache.get(uid, {})}), content_type="application/json")
