from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler, ExtractDataXls, search_text
from django.contrib import messages
import json
from django.shortcuts import redirect
from django.urls import reverse
import re
from .utils import BaseView
from .models import Iplist, Tags
from django.core.paginator import Paginator

class IpTable(BaseView, View):
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
            data = Iplist.objects.filter(tags__id=page_dataset)
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
