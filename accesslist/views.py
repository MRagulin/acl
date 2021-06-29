from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from .models import ACL
from ownerlist.models import Owners, Iplist
import os
from ownerlist.utils import make_doc, MakeMarkDown, request_handler, is_valid_uuid, ip_status, logger, get_client_ip
from ownerlist.utils import FORM_APPLICATION_KEYS, FORM_URLS, BaseView, GitWorker, BASE_DIR, UpdateCallBackStatus
import json
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
import re
import threading
import sys
from time import sleep

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
                    request.session['taskid'] = None
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
                request.session['taskid'] = tmp.taskid or ''

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
            if acl_id is not None:
                if request.user.is_staff:
                    acllist= ACL.objects.filter(id__exact=acl_id)
                else:
                    acllist = ACL.objects.filter(id__exact=acl_id, owner__email__iexact=request.user.email)
            else:
                if request.user.is_staff:
                    acllist = ACL.objects.order_by("-created", "-pkid")
                else:
                    acllist = ACL.objects.filter(owner_id=request.user.id).order_by("-created", "-pkid") #owner__email__iexact=request.user.email

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


class Acl_approve(ObjectMixin, View):
    template = 'acl_approve.html'
    url = 'acl_approve_urls'

class Acl_pending(View):
    """Функция вывода информации об согласовании объекта"""
    def get(self, request, acl_id=None):
        if acl_id is None:
            return redirect(reverse(FORM_URLS[1]))

        tmp = get_object_or_404(ACL, id=str(acl_id))
        tmp = json.loads(tmp.acltext)
        context = {'acl_id': str(acl_id),
                   'LOCAL_STORAGE': tmp}

        return render(request, 'acl_pending.html', context=context)

class AclDemo(BaseView, View):
    """Страница приветствия"""
    def get(self, request):
        request.session['LOCAL_STORAGE'] = {}
        request.session['uuid'] = 0
        request.session['taskid'] = None
        if 'GIT_URL' in request.session:
           del request.session['GIT_URL']

        if 'file_download' in request.session:
            try:
                BASE = os.path.basename(request.session['file_download'])
                if BASE:
                    BASE = os.path.join(settings.BASE_DIR, 'static//docx//' + BASE)
                    if os.path.exists(BASE):
                        os.remove(BASE)
            finally:
                del request.session['file_download']
                BASE = None

        if 'file_download_md' in request.session:
            try:
                BASE = os.path.basename(request.session['file_download_md'])
                if BASE:
                    BASE = os.path.join(settings.BASE_DIR, 'static//md//' + BASE)
                    if os.path.exists(BASE):
                        os.remove(BASE)
            finally:
                del request.session['file_download_md']
                BASE = None






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
            #if created:
            if len(request.session['LOCAL_STORAGE']) <= 1:
                    obj.status = 'NOTFL'
            else:
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
        if acl_id is None or 'LOCAL_STORAGE' not in request.session or 'uuid' not in request.session:
            return HttpResponseRedirect(reverse('acldemo_urls'))

        context = {'obj': acl_id,
                   'file_download': None,
                   'file_md': None,
                   'gitproc': None
                   }
        # obj = None
        # file_download = None
        # file_md = None
        # gitproc = None
        if 'uuid' in request.session is not None:
                    if '/new/' in request.path:
                        if str(acl_id) != request.session['uuid']:
                            return HttpResponseRedirect(reverse(FORM_URLS[0]))
                    elif str(acl_id) == request.session['uuid']:
                        return redirect(reverse('acloverview_urls', kwargs={'acl_id': request.session['uuid']}))

        """Проверяем состояние массива с данными"""
        if len(request.session['LOCAL_STORAGE']) >= 1: #and all(KEY in request.session['LOCAL_STORAGE'] for KEY in FORM_APPLICATION_KEYS):
                # if 'action_make_docx' in request.session:
                #             file_download = 'None'
                #             try:
                #                 file_download = make_doc(request, request.session['LOCAL_STORAGE'], str(acl_id))
                #                 request.session['file_download'] = file_download
                #                 del request.session['action_make_docx']
                #
                #             except PermissionError:
                #                 messages.error(request, 'К сожалению, мы не смогли создать файл, так как нехватает прав.')
                #                 logger.warning('Ошибка при создании файла')
                #             except Exception as e:
                #                 messages.error(request, 'К сожалению, при создании файла, что-то пошло не так. '
                #                                         'Мы уже занимаемся устранением. {}'.format(e))
                #
                # if 'action_make_git' in request.session:
                #     file_md = MakeMarkDown(request.session['LOCAL_STORAGE'], 'acl_{}'.format(str(acl_id))) or 'None'
                #     file_md_abs = os.path.join(BASE_DIR, 'static/md/' + 'acl_{}'.format(str(acl_id)) + '.md')
                #     request.session['file_download_md'] = file_md
                #     del request.session['action_make_git']
                #
                #     if 'GIT_URL' in request.session:
                #             if 'GIT_USERNAME' in request.session and 'GIT_PASSWORD' in request.session:
                #                 GitWorketAsync(request,
                #                 request.session['GIT_URL'], request.session['GIT_USERNAME'],
                #                 request.session['GIT_PASSWORD'], None, file_md_abs)
                #
                #                 gitproc = list(self.request.session['GIT_STATUS'])[-1]
                #
                # owner_form = request.session['LOCAL_STORAGE'][FORM_APPLICATION_KEYS[0]]
                # obj = save__form(request, owner_form, acl_id)
                #
                # del request.session['uuid']
                # del request.session['LOCAL_STORAGE']
                # del request.session['taskid']
                # if 'GIT_URL' in request.session:
                #     del request.session['GIT_URL']

                #-------------------------------------------------------------------------------------------------------

                if 'ACT_MAKE_DOCX' in request.session:
                    #request.session['docx_download_status'] = True
                    context['file_download'] = True

                    #t = threading.Thread(target=make_doc, args=[request, request.session['LOCAL_STORAGE'], str(acl_id)])
                    #t.setDaemon(True)
                    #t.start()
                if 'ACT_MAKE_GIT' in request.session:
                    #request.session['git_upload_status'] = True
                    context['gitproc'] = True

                owner_form = request.session['LOCAL_STORAGE'][FORM_APPLICATION_KEYS[0]]
                obj = save__form(request, owner_form, acl_id)


                #-------------------------------------------------------------------------------------------------------
                #ExemineTask()
        #if obj:

        return render(request, 'acl_overview.html', context=context)
        # else:
        #     return render(request, 'acl_overview.html', context={'file_download': file_download,
        #                                                          'file_md': file_md,
        #                                                          'gitproc': gitproc,
        #                                                          'acl_id': acl_id})

@csrf_exempt
def AclStageChange(request,  *args, **kwargs):
    if request.method == 'POST':
        #messages.info(request, 'Статус изменен')
        result = {'status': 'Статус изменен'}

        uuid =  request.POST.get('uuid', '')
        text = request.POST.get('text', '')
        stage = request.POST.get('stage', '')

        if (uuid!= '' and is_valid_uuid(uuid) and stage!=''):
                try:
                   acl = ACL.objects.get(id = uuid)
                   if acl:
                       acl.status = stage
                       acl.taskid = text
                       acl.save()

                except ACL.DoesNotExist:
                    return HttpResponse(json.dumps('Ошибка, таких данных нет'), content_type="application/json")

                return HttpResponse(json.dumps(result), content_type="application/json")
        return HttpResponse(json.dumps('Ошибка данных'), content_type="application/json")
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
