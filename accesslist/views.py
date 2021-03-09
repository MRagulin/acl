from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from .models import ACL
from ownerlist.models import Owners
from django.db.utils import IntegrityError

from ownerlist.utils import make_doc, request_handler
from ownerlist.utils import LOCAL_ACTION, FORM_APPLICATION_KEYS, POST_FORM_KEYS,  FORM_URLS, LOCAL_UID, LOCAL_STORAGE, \
    ip_status

import json
import uuid

import ipaddress
class ObjectMixin:
    template = None
    url = None

    def get(self, request, acl_id=None):
        global LOCAL_UID
        global LOCAL_STORAGE

        if acl_id is None:
            if LOCAL_UID is not None:
                return redirect(reverse(self.url, kwargs={'acl_id': LOCAL_UID}))

            if 'HTTP_REFERER' in request.META.keys():
                if reverse(FORM_URLS[0]) in request.META.get('HTTP_REFERER'):
                    LOCAL_UID = str(uuid.uuid4())
                    return HttpResponseRedirect(reverse(FORM_URLS[1], kwargs={'acl_id': LOCAL_UID}))
        else:
            if LOCAL_UID is None:
                LOCAL_UID = acl_id
            try:
                tmp = ACL.objects.get(id=str(acl_id))
                LOCAL_STORAGE = json.loads(tmp.acltext)
            except ACL.DoesNotExist:
                pass

            if self.template not in LOCAL_STORAGE:
                return render(request, self.template, context={'acl_id': acl_id})
            else:
                return render(request, self.template, context={'acl_id': acl_id, 'LOCAL_STORAGE': LOCAL_STORAGE[self.template]})
        return HttpResponseRedirect(reverse(FORM_URLS[0]))

    def post(self, request, acl_id=None):
        global LOCAL_STORAGE
        #request.method == 'POST' and request.is_ajax
        if acl_id is not None:
            tmp = request_handler(request, self.template)
            if tmp:
                if self.template in LOCAL_STORAGE:
                    LOCAL_STORAGE.update({self.template: tmp[self.template]})
                else:
                    LOCAL_STORAGE[self.template] = tmp[self.template]
                obj, created = ACL.objects.get_or_create(id=str(acl_id))
                obj.acltext = json.dumps(LOCAL_STORAGE)
                obj.save()

                #if created:
            current_page = FORM_URLS.index(self.url)
            return redirect(reverse(FORM_URLS[current_page + 1], kwargs={'acl_id': acl_id}))

        messages.warning(request, 'Не все поля заполнены')
        return render(request, self.template)


class Aclhistory(View):
    def get(self, request, acl_id=None):
        if acl_id is not None:
            acllist= ACL.objects.filter(id__exact=acl_id)
        else:
            acllist = ACL.objects.order_by("-created")[:10]
        return render(request, 'acl_history.html', context={"acllists": acllist})


class AclCreate(ObjectMixin, View):
    template = 'acl_create_info.html'
    url = 'aclcreate_urls'


class AclCreate_internal(ObjectMixin, View):
    template = 'acl_internal_resources.html'
    url = 'aclinternal_urls'


class AclCreate_dmz(ObjectMixin, View):
    template = 'acl_dmz_resources.html'
    url = 'acldmz_urls'


class AclCreate_external(ObjectMixin, View):
    template = 'acl_external_resources.html'
    url = 'aclexternal_urls'


class AclCreate_traffic(ObjectMixin, View):
    template = 'acl_traffic.html'
    url = 'acltraffic_urls'


class AclTest(View):
    def get(self, request):
        return render(request, 'acl_test.html')


class AclDemo(View):
    def get(self, request):
        global LOCAL_UID
        global LOCAL_STORAGE

        LOCAL_UID = None
        LOCAL_STORAGE = {}
        return render(request, 'acl_demo.html')


def ACldefault(request):
    return HttpResponseRedirect(reverse('acldemo_urls'))


class AclOver(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        global LOCAL_STORAGE

        if acl_id is None:
            if LOCAL_UID is not None:
                return redirect(reverse('acloverview_urls', kwargs={'acl_id': LOCAL_UID}))
            else:
                return HttpResponseRedirect(reverse('acldemo_urls'))

        file_download = None
        if len(LOCAL_STORAGE) >= 4 and all(KEY in LOCAL_STORAGE for KEY in FORM_APPLICATION_KEYS):
            try:
                file_download = make_doc(request, LOCAL_STORAGE, str(acl_id))
            except PermissionError:
                messages.error(request, 'К сожалению, мы не смогли создать файл, так как нехватает прав.')
            except Exception as e:
                messages.error(request, 'К сожалению, при создании файла, что-то пошло не так. '
                                        'Мы уже занимаемся устранением. {}'.format(e))
            owner_form = LOCAL_STORAGE[FORM_APPLICATION_KEYS[0]]

            #try:
            user, created = Owners.objects.get_or_create(email=owner_form[1])
            if created:
                    user.username = owner_form[0],
                    user.phone = owner_form[2],
                    user.active = True,
                    user.department = owner_form[3]
                    user.save()
            # except:
            #     pass
            #except IntegrityError:
                # user = Owners.objects.get(email=owner_form[1])
                # user.username = owner_form[0]
                # user.phone = owner_form[2]
                # user.department = owner_form[3]
                # user.save()
               # pass
            try:
                obj, created = ACL.objects.get_or_create(id=str(acl_id))
                if obj:
                    obj.acltext = json.dumps(LOCAL_STORAGE)
                    obj.is_executed = False
                    obj.status = 'FL'
                    obj.owner = user
                    obj.project = owner_form[4]
                    obj.save()


            except Exception as e:
                messages.error(request, 'Ошибка, мы не смогли записать данные в БД. {}'.format(e))

            # Очищаем глобальный массив с данными для заполнения docx
            LOCAL_STORAGE = {}
            LOCAL_UID = None
        #test = json.dumps(LOCAL_STORAGE)
        #return HttpResponse("{} {}".format(test, LOCAL_STORAGE))
        return render(request, 'acl_overview.html', context={'file_download': file_download})



def CheckIp(request, ip=None):
    return HttpResponse(json.dumps(ip_status(ip)), content_type="application/json")