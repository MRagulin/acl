from django.shortcuts import render
from django.views.generic import View


class AclTest(View):
    def get(self, request):
        return render(request, 'acl_test.html')

class AclOver(View):
    def get(self, request):
        return render(request, 'acl_overview.html')

class AclCreate(View):
    def get(self, request):
        #context = {'welcome': True}
        #stage = request.path.split('/')[4].strip()
        #if stage == '':
        return render(request, 'acl_create_info.html')
        #else:
        #return render(request, 'acl_create_'+stage+'.html', context=context)

# class AclInfo(View):
#     def get(self, request):
#         return render(request, 'acl_create_info.html')


class AclCreate_StageOne(View):
    def get(self, request):
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