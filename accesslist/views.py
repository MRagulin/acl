from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from .models import ACL

from ownerlist.utils import make_doc, request_handler
from ownerlist.utils import LOCAL_STORAGE, LOCAL_ACTION, FORM_APPLICATION_KEYS, POST_FORM_KEYS, LOCAL_UID

import json
import uuid

#
# class ObjectMixin:
#     model = None
#     template = None
#     next_step = None
#     obj = None
#     context = {}
#
#     def get(self, request, acl_id=None):
#         global LOCAL_UID
#         if acl_id is None:
#             if 'HTTP_REFERER' in request.META.keys():
#                 if reverse('acldemo_urls') in request.META.get('HTTP_REFERER'):
#                     LOCAL_UID = str(uuid.uuid4())
#                     return HttpResponseRedirect(reverse('aclcreate_uuid_urls', kwargs={'acl_id': LOCAL_UID}))
#         else:
#             #if reverse('aclcreate_urls') not in request.path:
#                 #self.obj = get_object_or_404(self.model, id=acl_id)
#             if acl_id == LOCAL_UID:
#                 self.context['acl_id'] = LOCAL_UID
#                 self.context[self.model.__name__.lower()] = self.obj
#                 return render(request, self.template, context=self.context)
#
#         return HttpResponseRedirect(reverse('acldemo_urls'))
#
#     def post(self, request, acl_id=None):
#         if request.is_ajax and acl_id is not None and (acl_id == LOCAL_UID) and request_handler(request, self.template):
#             return redirect(reverse(self.next_step, kwargs={'acl_id': acl_id}))
#         else:
#              messages.warning(request, 'Не все поля заполнены')
#              return render(request, self.template)
#
#
# class AclCreate(ObjectMixin, View):
#     model = ACL
#     template = 'acl_create_info.html'
#     next_step = 'aclinternal_urls'
#
# class AclCreate_internal(ObjectMixin, View):
#     model = ACL
#     template = 'acl_internal_resources.html'
#     next_step = 'acldmz_urls'
#
#
# class AclCreate_dmz(ObjectMixin, View):
#     model = ACL
#     template = 'acl_dmz_resources.html'
#     next_step = 'aclexternal_urls'


class AclTest(View):
    def get(self, request):
        return render(request, 'acl_test.html')

class AclDemo(View):
    def get(self, request):
        return render(request, 'acl_demo.html')

class AclOver(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        if acl_id is None:
            if LOCAL_UID is not None:
                return redirect(reverse('acloverview_urls', kwargs={'acl_id': LOCAL_UID}))
            else:
                return HttpResponseRedirect(reverse('acldemo_urls'))

        global LOCAL_STORAGE

        file_download = None
        if len(LOCAL_STORAGE) >= 4 and all(KEY in LOCAL_STORAGE for KEY in FORM_APPLICATION_KEYS):
            try:
                file_download = make_doc(request, LOCAL_STORAGE, str(acl_id))
            except PermissionError:
                messages.error(request, 'К сожалению, мы не смогли создать файл, так как нехватает прав.')
            except Exception as e:
                messages.error(request, 'К сожалению, при создании файла, что-то пошло не так. '
                                        'Мы уже занимаемся устранением. {}'.format(e))

            try:
                obj, created = ACL.objects.get_or_create(id=str(acl_id),
                                                         acltext=json.dumps(LOCAL_STORAGE),
                                                         is_executed=True)
            except Exception as e:
                messages.error(request, 'Ошибка, мы не смогли записать данные в БД. {}'.format(e))


            # Очищаем глобальный массив с данными для заполнения docx
            #LOCAL_STORAGE = {}
            #LOCAL_UID = None
        test = json.dumps(LOCAL_STORAGE)
        #return HttpResponse("{} {}".format(test, LOCAL_STORAGE))
        return render(request, 'acl_overview.html', context={'file_download': file_download})


class AclCreate(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        if acl_id is None:
            if 'HTTP_REFERER' in request.META.keys():
                if reverse('acldemo_urls') in request.META.get('HTTP_REFERER'):
                    LOCAL_UID = str(uuid.uuid4())
            if LOCAL_UID is not None:
                return HttpResponseRedirect(reverse('aclcreate_urls', kwargs={'acl_id': LOCAL_UID}))
        else:
            return render(request, 'acl_create_info.html', context={'acl_id': acl_id})
        return HttpResponseRedirect(reverse('acldemo_urls'))


    def post(self, request, acl_id=None):
        if request.method == 'POST' and request.is_ajax and acl_id is not None and request_handler(request, 'acl_create_info.html'):
            return redirect(reverse('aclinternal_urls', kwargs={'acl_id': acl_id}))
            #return redirect('AclCreate_internal', acl_id=acl_id)
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_create_info.html')

# class AclInfo(View):
#     def get(self, request):
#         return render(request, 'acl_create_info.html')


def ACldefault(request):
    return HttpResponseRedirect(reverse('acldemo_urls'))


class AclCreate_internal(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        if acl_id is None:
           if LOCAL_UID is not None:
               return redirect(reverse('aclinternal_urls', kwargs={'acl_id': LOCAL_UID}))
           else:
               return HttpResponseRedirect(reverse('acldemo_urls'))
        return render(request, 'acl_internal_resources.html', context={'acl_id': acl_id})

    def post(self, request, acl_id=None):
        if request.method == 'POST' and request.is_ajax and acl_id is not None and request_handler(request, 'acl_internal_resources.html'):
            return HttpResponseRedirect(reverse('acldmz_urls', kwargs={'acl_id': acl_id}))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_internal_resources.html')



class AclCreate_dmz(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        if acl_id is None:
            if LOCAL_UID is not None:
                return redirect(reverse('acldmz_urls', kwargs={'acl_id': LOCAL_UID}))
            else:
                return HttpResponseRedirect(reverse('acldemo_urls'))
        return render(request, 'acl_dmz_resources.html', context={'acl_id': acl_id})

    def post(self, request, acl_id=None):
        if request.method == 'POST' and request.is_ajax and acl_id is not None and request_handler(request, 'acl_dmz_resources.html'):
            return HttpResponseRedirect(reverse('aclexternal_urls', kwargs={'acl_id': acl_id}))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_dmz_resources.html')


class AclCreate_external(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        if acl_id is None:
            if LOCAL_UID is not None:
                return redirect(reverse('aclexternal_urls', kwargs={'acl_id': LOCAL_UID}))
            else:
                return HttpResponseRedirect(reverse('acldemo_urls'))
        return render(request, 'acl_external_resources.html', context={'acl_id': acl_id})

    def post(self, request, acl_id=None):
        if request.method == 'POST' and request.is_ajax and acl_id is not None and request_handler(request, 'acl_external_resources.html'):
            return HttpResponseRedirect(reverse('acltraffic_urls', kwargs={'acl_id': acl_id}))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_external_resources.html')


class AclCreate_traffic(View):
    def get(self, request, acl_id=None):
        global LOCAL_UID
        if acl_id is None:
            if LOCAL_UID is not None:
                return redirect(reverse('acltraffic_urls', kwargs={'acl_id': LOCAL_UID}))
            else:
                return HttpResponseRedirect(reverse('acldemo_urls'))
        return render(request, 'acl_traffic.html', context={'acl_id': acl_id})

    def post(self, request, acl_id=None):
        if request.method == 'POST' and request.is_ajax and acl_id is not None and request_handler(request, 'acl_traffic.html'):
            return HttpResponseRedirect(reverse('acloverview_urls', kwargs={'acl_id': acl_id}))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_traffic.html')