import os, sys
from pathlib import Path
from django.core.files.storage import FileSystemStorage
from django.apps import apps
import socket
import re
import xlrd
from django.conf import settings
#from .models import Vlans, Tags, Owners, Iplist


BASE_DIR = Path(__file__).resolve().parent.parent

#Function convert IP to integer
def IP2Int(ip):
    o = list(map(int, ip.split('.')))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res

#Funtion file upload to server handler
def upload_file_handler(request, functionhandler = None):
    result = {}
    if 'FileInput' in request.FILES:
        UPLOAD_PATH = os.path.join(BASE_DIR, 'upload')
        myfile = request.FILES['FileInput']
        fs = FileSystemStorage(location=UPLOAD_PATH)
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = os.path.join(UPLOAD_PATH, myfile.name) #bug with persone encode
       # uploaded_file_url = '{}{}'.format(UPLOAD_PATH, fs.url(filename))

        result['ok'] = "File start processing..."
        print('Upload file to: {}'.format(uploaded_file_url))
    else:
        result['error'] = "There is error upload file"

    if functionhandler is not None:
        return functionhandler(uploaded_file_url)
    else:
        vlan_fun = ExtractDataXls(uploaded_file_url)
        return vlan_fun.ExtractVlanInfo()
        #print("[E] Function handler not defined")
        #return result



def ExcelHandler(filename = ''):
    ext = filename.split(".")[-1].lower()
    print(ext)
    if ext == 'xls': #old format
        return ExtractDataXls(filename)
    else:
        if ext == 'xlsx': #new format
            from openpyxl import load_workbook
            print('Open File: {}'.format(filename))
            wb = load_workbook(filename)
            print("Sheets: {}".format(wb.get_sheet_names()))
        else:
            print('File not supported :(')

def is_row_empty(row):
    result = True
    for d in row:
        if d != '':
            result = False
            break
    return result

def gethostname(ip):
    result = socket.gethostbyaddr(ip)
    if len(result) > 1:
        return result[0]
    else:
        return ''

def isvalidip(ip, page_name = ''):
    l = len(str(ip));
    if (l ==0) or (l > 15): return False
    s = str(ip).split('.')
    if len(s) >= 3:
        return True
    else:
        return False


def get_ip_from_page(page):
    try:
        ip = re.findall(r"(\d{1,3})", page)
        return ".".join(page)
    except:
        pass
    return ""





class ExtractDataXls():
    def __init__(self, filename=''):
        self.ip_addr_idx = 1
        self.count_total: int = 0 #total records in db
        self.error_count: int = 0 #total errors
        self.rb = xlrd.open_workbook(filename, formatting_info=True)
        self.current_page = ''
        self.sheet_tags = self.rb.sheet_names()

    def execute_file_parsing(self):
        """Выбираем парсер на основе имени страницы"""
        for self.sheet_tag in self.sheet_tags:
            if self.sheet_tag == 'VLAN DESCRIPTION':
                self.ExtractVlanInfo()
            elif self.sheet_tag == 'VLAN_CORE_ACI':
                self.ExtractVlanInfo(name_idx=6, location_idx=3, vlan_idx=2, subnet_idx=4, mask_idx=5, tag1_idx=7, tag2_idx=8)

    def is_row_empty(self, row) -> bool:
        """ Проверяем пустая ли запись"""
        result = True
        for d in row:
            if d != '':
                result = False
                break
        return result

    def get_ip_from_page(self, page) -> str:
        """Получаем полный IP из имени страницы"""
        try:
            ip = re.findall(r"(\d{1,3})", page)
            return ".".join(ip)
        except:
            pass
        return ""

    def ExtractVlanInfo(self, name_idx = 1, location_idx = 2, vlan_idx = 3, subnet_idx = 4, mask_idx = 5, tag1_idx = 6, tag2_idx = 7) -> int:
        """Парсер страницы с описанием VLAN"""
        row_index: int = 0
        tags: list = []
        Vlans = apps.get_model('ownerlist', 'Vlans')
        Tags = apps.get_model('ownerlist', 'Tags')

        self.current_page = self.rb.sheet_by_name(self.sheet_tag)
        if self.current_page.nrows > 0: #Count row
                    for row_idx in range(self.current_page.nrows):
                        row = self.current_page.row_values(row_idx)
                        if row_idx == 0 or self.is_row_empty(row):
                            continue

                        if type(row[vlan_idx]) == float:
                            vlan = int(round(row[vlan_idx]))
                        elif type(row[vlan_idx]) == str:
                             try:
                                   vlan = int(round(float(row[vlan_idx])))
                             except ValueError:
                                    vlan = 0

                        if str(row[subnet_idx]).find('/') > 0:
                                subnet = str(row[subnet_idx]).split('/')
                                subnet, mask = subnet[0], int(subnet[1])
                        else:
                            try:
                                if len(str(row[subnet_idx])) > 15:
                                    subnet = str(row[subnet_idx]).split('\n')[0] #Bug fig, if a couple value in row
                                else:
                                    subnet = str(row[subnet_idx])
                            except ValueError:
                                subnet = 0


                            try:
                                if len(str(row[mask_idx])) > 4:
                                    mask = str(row[mask_idx]).split('\n')[0] #Bug fig, if a couple value in row
                                    mask = int(round(float(mask)))
                                else:
                                    mask = int(round(float(row[mask_idx]))) or 0
                            except ValueError:
                                mask = 0

                        vlan_info, _ = Vlans.objects.get_or_create(
                        name=str(row[name_idx]),
                        location=str(row[location_idx]),
                        vlan=vlan,
                        subnet=subnet,
                        mask=mask,
                        )

                        if _: #if created obj
                                self.count_total += 1

                        try:
                            tags.append(self.sheet_tag)
                            tags.append(row[tag1_idx])
                            tags.append(row[tag2_idx])

                            for tag in tags:
                                if (tag != '') and len(tag) > 1:
                                            if len(str(tag).split('.')) >= 3:  # If tag as Gateway's IP
                                                tag = "Gateway: {}".format(tag)
                                            tag_info, _ = Tags.objects.get_or_create(name=str(tag).rstrip())
                                            if tag_info not in vlan_info.tags.all():
                                                vlan_info.tags.add(tag_info)
                                                self.count_total += 1
                        except:
                            pass

                        finally:
                            tags.clear()

        if settings.DEBUG == True:
            print("Добавленно {} новых записей в БД.".format(self.count_total))

        return self.count_total
