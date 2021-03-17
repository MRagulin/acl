from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from .models import ACL
from ownerlist.models import Owners
import os
from pathlib import Path
from ownerlist.utils import make_doc, request_handler, is_valid_uuid, ip_status
from ownerlist.utils import FORM_APPLICATION_KEYS, FORM_URLS, BaseView
import json
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


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
                    request.session['uuid'] = str(uuid.uuid4())
                    request.session['LOCAL_STORAGE'] = {}
                    return HttpResponseRedirect(reverse(FORM_URLS[1], kwargs={'acl_id': request.session['uuid']}))
        else:
            if 'uuid' in request.session is not None:
                  if '/new/' in request.path:
                      if str(acl_id) != request.session['uuid']:
                         return HttpResponseRedirect(reverse(FORM_URLS[0]))
                  elif str(acl_id) == request.session['uuid']:
                     return redirect(reverse(self.url, kwargs={'acl_id': request.session['uuid']}))

            if '/new/' not in request.path:
                tmp = get_object_or_404(ACL, id=str(acl_id))
                request.session['LOCAL_STORAGE'] = json.loads(tmp.acltext)
                request.session['action_make_docx'] = True

            context = {'acl_id': str(acl_id),
                       'FULL_STORAGE': request.session['LOCAL_STORAGE'],
                       'FORM_APPLICATION_KEYS': FORM_APPLICATION_KEYS,
                       'template_name': self.template,
                       }

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
            if tmp:
                if self.template in request.session['LOCAL_STORAGE']:
                    request.session['LOCAL_STORAGE'].update({self.template: tmp[self.template]})
                else:
                    request.session['LOCAL_STORAGE'][self.template] = tmp[self.template]

                current_page = FORM_URLS.index(self.url)
                request.session.modified = True
                if '/new/' in request.path:
                    if 'uuid' not in request.session or request.session['uuid'] != str(acl_id):
                        return redirect(reverse(FORM_URLS[current_page + 1], kwargs={'acl_id': acl_id}))
                    else:
                        HttpResponseRedirect(reverse(FORM_URLS[0]))

                owner_form = request.session['LOCAL_STORAGE'][FORM_APPLICATION_KEYS[0]]
                save__form(request, owner_form, acl_id)
                return redirect("{}{}/".format(reverse(FORM_URLS[current_page + 1]), acl_id))

        messages.warning(request, 'Не все поля заполнены')
        return render(request, self.template, context={'acl_id': acl_id})


class Aclhistory(BaseView, View):
    """История запросов"""
    def get(self, request, acl_id=None):
            if acl_id is not None:
                acllist= ACL.objects.filter(id__exact=acl_id)
            else:
                acllist = ACL.objects.order_by("-created", "-pkid")
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


class AclCreate_traffic(BaseView, ObjectMixin, View):
    template = 'acl_traffic.html'
    url = 'acltraffic_urls'


class AclDemo(BaseView, View):
    """Страница приветствия"""
    def get(self, request):
        request.session['LOCAL_STORAGE'] = {}
        request.session['uuid'] = 0
        if 'file_download' in request.session:
                BASE = os.path.join(Path(__file__).resolve().parent.parent)
                BASE += os.path.join(request.session['file_download'])
                if os.path.exists(BASE):
                    os.remove(BASE)
                del request.session['file_download']
        return render(request, 'acl_demo.html')


def ACldefault(BaseView, request):
    request.session.set_expiry(0)
    return HttpResponseRedirect(reverse('acldemo_urls'))


def save__form(request, owner_form:None, acl_id)->None:
    """Сохранение данныех из сесии в БД"""
    user, created = Owners.objects.get_or_create(email=owner_form[1])
    if created:
        user.username = owner_form[0]
        user.phone = owner_form[2]
        user.active = True
        user.department = owner_form[3]
        user.save()
    try:
        obj, created = ACL.objects.get_or_create(id=str(acl_id))
        if obj:
            obj.acltext = json.dumps(request.session['LOCAL_STORAGE'])
            obj.is_executed = False
            obj.status = 'FL'
            obj.owner = user
            obj.project = owner_form[4]
            obj.save()

    except Exception as e:
        messages.error(request, 'Ошибка, мы не смогли записать данные в БД. {}'.format(e))


class AclOver(BaseView, View):
    """Страница формирования ACL файла и других активностей"""
    def get(self, request, acl_id=None):
        if acl_id is None or 'LOCAL_STORAGE' not in request.session or 'uuid' not in request.session:
            return HttpResponseRedirect(reverse('acldemo_urls'))
        obj = None
        file_download = None
        if '/new/' in request.path:
            if 'uuid' in request.session and request.session['uuid'] != str(acl_id):
                HttpResponseRedirect(reverse(FORM_URLS[0]))
        """Проверяем состояние массива с данными"""
        if len(request.session['LOCAL_STORAGE']) >= 4 and all(KEY in request.session['LOCAL_STORAGE'] for KEY in FORM_APPLICATION_KEYS):
                if 'action_make_docx' in request.session:
                            file_download = 'None'
                            try:
                                file_download = make_doc(request, request.session['LOCAL_STORAGE'], str(acl_id))
                                request.session['file_download'] = file_download
                                del request.session['action_make_docx']

                            except PermissionError:
                                messages.error(request, 'К сожалению, мы не смогли создать файл, так как нехватает прав.')
                            except Exception as e:
                                messages.error(request, 'К сожалению, при создании файла, что-то пошло не так. '
                                                        'Мы уже занимаемся устранением. {}'.format(e))
                owner_form = request.session['LOCAL_STORAGE'][FORM_APPLICATION_KEYS[0]]
                save__form(request, owner_form, acl_id)

                del request.session['uuid']
                del request.session['LOCAL_STORAGE']

        if obj:
            return render(request, 'acl_overview.html', context={'file_download': file_download, 'obj': obj.id})
        else:
            return render(request, 'acl_overview.html', context={'file_download': file_download, 'acl_id': acl_id})


def CheckIp(request, ip=None):
    """Функция возвращает данные по IP"""
    return HttpResponse(json.dumps(ip_status(ip)), content_type="application/json")

@csrf_exempt
def AclRemove(request, *args, **kwargs):
    """Функция удалеяет данные по uuid"""
    if request.method == 'POST':
        result = {'status': 'Запись удалена'}
        if 'data' in request.POST:
                if is_valid_uuid(request.POST.get('data')):
                       try:
                            obj = ACL.objects.get(id=request.POST.get('data'))
                            obj.delete()
                       except ACL.DoesNotExist:
                            result = {'error': 'Не всё записи удалены'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)