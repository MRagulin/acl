from django.shortcuts import render
from django.views.generic import View


class AclOver(View):
    def get(self, request):
        return render(request, 'acl_overview.html')

class AclCreate(View):
    def get(self, request):
        #context = {'welcome': True}
        #stage = request.path.split('/')[4].strip()
        #if stage == '':
        return render(request, 'acl_create.html')
        #else:
        #return render(request, 'acl_create_'+stage+'.html', context=context)

# class AclInfo(View):
#     def get(self, request):
#         return render(request, 'acl_create_info.html')