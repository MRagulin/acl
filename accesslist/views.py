from django.shortcuts import render
from django.views.generic import View
from ownerlist.utils import make_doc
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

data:dict = {}
act:dict = {}
post_name_forms_key = [['name', 'email', 'tel', 'department', 'project', 'd_form', 'd_start', 'd_complete']]
INFINITY = 'Нет'

def request_handler(requests, namespace = ''):
    global data

    if namespace == 'contact':
        con_list = []
        for idx, post_key in enumerate(post_name_forms_key[0]):
            if idx == 7: #post_key == 'd_complete'
                if requests.POST.get(post_key) == 'on':
                    con_list.append(INFINITY)
            else:
                if requests.POST.get(post_key) != '':
                    con_list.append(requests.POST.get(post_key))
                else:
                    return False
        data = {namespace: con_list}

    elif namespace == 'internal':
        con_list:list = []
        data[namespace] = []
        for k, v in requests.POST.items():
            if 'input_' in str(k):
                 if 'input__ip' in str(k):
                    if len(con_list) > 0:
                        if namespace in data:
                            data[namespace].append(con_list)
                            con_list.clear()
                        else:
                             data[namespace] = [con_list, ]
                             con_list.clear()
                 if v != '':
                        con_list.append(v)
                 else:
                     return False





    return True

class AclTest(View):
    def get(self, request):
        return render(request, 'acl_test.html')

class AclOver(View):
    def get(self, request):
        global data
        # data['contact'] = ['Рагулин Михаил Пиздабольевич', 'ragulinma@alfastrah.ru', '8(909)6971821', 'УИБ', 'Портал',
        #                    '18.02.2021', '28.02.2021', 'Нет']
        #
        # data['internal'] = [['172.16.1.1', '24', 'Внутренняя сеть AC'],
        #                     ['172.16.1.2', '24', 'Внутренняя сеть Кемерово']]
        #
        # data['dmz'] = [['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Public'],
        #                ['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Wild']]
        #
        # data['external'] = [['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Public'],
        #                     ['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Wild']]
        #
        # data['traffic'] = [['dpgw.alfastrah.ru', '195.239.64.162', 'Z14-1709-gw.alfastrah.ru', '195.239.64.79',
        #                     'TCP: 80,443,9000-9100', 'Функционал авто-ризации через ЕСИА 2.0'],
        #                    ['Z14-1709-gw.alfastrah.ru', '195.239.64.79',
        #                     'gosuslugi.ru www.gosuslugi.ru esia.gosuslugi.ru esia-por-tal1.test.gosuslugi.ru esia-por',
        #                     '-', 'TCP: 443', 'Доступ к ГИС']]

        file_download = make_doc(data)
        data = {}
        return render(request, 'acl_overview.html', context={'file_download': file_download})

class AclCreate(View):
    def get(self, request):
        return render(request, 'acl_create_info.html')
    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'contact'):
            return HttpResponseRedirect(reverse('aclinternal_urls'))
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_create_info.html')

# class AclInfo(View):
#     def get(self, request):
#         return render(request, 'acl_create_info.html')


class AclCreate_StageOne(View):
    def get(self, request):
        return render(request, 'acl_internal_resources.html')

    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'internal'):
            return HttpResponseRedirect(reverse('acldmz_urls'))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_internal_resources.html')



class AclCreate_StageTwo(View):
    def get(self, request):
        return render(request, 'acl_dmz_resources.html')


class AclCreate_StageThree(View):
    def get(self, request):
        return render(request, 'acl_external_resources.html')


class AclCreate_StageFour(View):
    def get(self, request):
        return render(request, 'acl_traffic.html')