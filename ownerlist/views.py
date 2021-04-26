from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from .forms import UploadFileForm
from .utils import upload_file_handler, ExtractDataXls, search_text
from django.contrib import messages
import json
from django.shortcuts import redirect
from django.urls import reverse
import re
from .utils import BaseView
from .models import Iplist, Tags, Owners
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import socket
from django.contrib.auth.mixins import LoginRequiredMixin

class IpTable(BaseView, LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        if not 'dataset' in request.GET:
            response = redirect(reverse('iptable_urls'))
            response['Location'] += '?dataset=1&&page=1'
            return response

        page_dataset = request.GET.get('dataset', 1)
        page_offset = request.GET.get('page', 1)

        if page_dataset is None:
            page_dataset = 1
        else:
            page_dataset = int(page_dataset)

        if page_dataset != 0:
            data = Iplist.objects.filter(tags__id=page_dataset).order_by('ipv4')
        else:
            data = Iplist.objects.filter(tags__id=1)

        paginator = Paginator(data, 15)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)

        is_paginated = page.has_other_pages()

        if page.has_previous():
                prev_url = '?dataset={}&&page={}'.format(page_dataset, page.previous_page_number())
        else:
                prev_url = ''

        if page.has_next():
                next_url = '?dataset={}&&page={}'.format(page_dataset,page.next_page_number())

        else:
            next_url = ''

        context = {
                "dataset": page,
                "page_dataset": page_dataset,
                "is_paginated": is_paginated,
                "url_mask": '?dataset={}&&page='.format(page_dataset),
                "next_url": next_url,
                "prev_url": prev_url
            }

        assets = Tags.objects.all()#[:15]
        context['assets'] = assets

        return render(request, 'iptable.html', context)

    def post(self, request):
        result = None
        try:
            result = upload_file_handler(request)
        except Exception as e:
            if request.is_ajax:
                result = {'error': str(e)}
            else:
                messages.error(request, str(e))

        if request.method == 'POST' and request.is_ajax:
            return HttpResponse(json.dumps(result), content_type="application/text")
        return render(request, 'iptable.html', context=result)

class TreeView(BaseView, View):
    def get(self, request):
        return render(request, 'index.html')


class SearchView(BaseView, View):
    def get(self, request):
        context = {}
        search = request.path.split('/')
        result = search[2].strip().lower()
        if result == '':
                return redirect('ipconfig_urls')
        if search is not None:
            if re.match(r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}", result):
                return redirect(reverse('aclhistory_urls', kwargs={'acl_id': result}))
            context = search_text(request, result)
        return render(request, 'search.html', context=context)


class Vpn(BaseView, View):
    def get(self, request):
        return render(request, 'vpn.html')

@csrf_exempt
def ip_resolve(request, *args, **kwargs):
    if request.method == 'POST':
        ip = request.POST.get('ip', '')
        result = {'status': ''}
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            return HttpResponseBadRequest('Неправильный IP-адрес')
        if ip:
            try:
                result = socket.gethostbyaddr(ip)
            except Exception as e:
                return HttpResponse(json.dumps(result), content_type="application/json")
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)


@csrf_exempt
def domain_resolve(request, *args, **kwargs):
    if request.method == 'POST':
        domain = request.POST.get('domain', '')
        result = {'status': ''}
        if not re.match(r"^(?=.{1,255}$)(?!-)[A-Za-z0-9\-]{1,63}(\.[A-Za-z0-9\-]{1,63})*\.?(?<!-)$", domain):
            return HttpResponseBadRequest('Неправильный домен')
        if domain:
            try:
                result = socket.gethostbyname(domain)
            except Exception as e:
                return HttpResponse(json.dumps(result), content_type="application/json")
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)


@csrf_exempt
def ip_delete(request, *args, **kwargs):
    if request.method == 'POST':
        idx = request.POST.get('idx')
        result = {'status': 'Данные удалены'}
        try:
            obj = Iplist.objects.get(id=idx)
            obj.delete()
        except Iplist.DoesNotExist:
            HttpResponseNotFound('IP адрес не найден')
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)

@csrf_exempt
def ip_save(request, *args, **kwargs):
    """Функция изменяет или создает данные по ip"""
    if request.method == 'POST':
        result = {'status': 'Данные сохранены'}
        if 'ip' in request.POST:
            ip = request.POST.get('ip')
            idx = request.POST.get('idx', '')
            tags = request.POST.get('asset', '')
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                return HttpResponseBadRequest('Неправильный IP-адрес')
            try:
                   if idx != '':
                        obj = Iplist.objects.get(id=idx)
                        obj.ipv4 = ip
                   else:
                       obj = Iplist.objects.create(ipv4=ip)
                   if tags == '':
                        tags = 'DEFAULT'
                   tag, created = Tags.objects.get_or_create(name=tags)
                   owner, created_obj = Owners.objects.get_or_create(username=request.POST.get('owner', ''))
                   if obj:
                        obj.hostname = request.POST.get('domain', '')
                        if owner:
                            obj.owner = owner
                        obj.comment = request.POST.get('comment', '')
                        if tag:
                            if idx != '':
                                obj.tags.add(*[tag.id])
                            else:
                                obj.tags.set([tag.id])
                        obj.save()

            except Iplist.DoesNotExist:
                 return HttpResponseNotFound('IP адрес не найден')
            except Exception as e:
                return HttpResponseNotFound(str(e))

        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(status=405)