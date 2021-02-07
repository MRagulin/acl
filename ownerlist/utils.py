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
    def __init__(self, filename= ''):
        self.ip_addr_idx = 1
        self.count_total = 0
        self.error_count = 0 #total errors
        self.rb = xlrd.open_workbook(filename, formatting_info=True)
        self.current_page = ''

    def is_row_empty(self, row):
        result = True
        for d in row:
            if d != '':
                result = False
                break
        return result

    def get_ip_from_page(self, page):
        try:
            ip = re.findall(r"(\d{1,3})", page)
            return ".".join(ip)
        except:
            pass
        return ""

    def ExtractVlanInfo(self) -> int:
        """Парсер страницы с описанием VLAN"""
        row_index: int = 0
        internal_count: int = 0
        self.sheet_tags = self.rb.sheet_names()
        Vlans = apps.get_model('ownerlist', 'Vlans')
        Tags = apps.get_model('ownerlist', 'Tags')

        for self.sheet_tag in self.sheet_tags:
            self.current_page = self.rb.sheet_by_name(self.sheet_tag)
            if self.current_page.nrows > 0: #Count row
                    for row_idx in range(self.current_page.nrows):
                        row = self.current_page.row_values(row_idx)
                        if row_idx == 0 or self.is_row_empty(row):
                            continue

                        if type(row[3]) == float:
                            vlan = int(round(row[3]))
                        elif type(row[3]) == str:
                             try:
                                   vlan = int(round(float(row[3])))
                             except ValueError:
                                    vlan = 0

                        if str(row[4]).find('/') > 0:
                                subnet = str(row[4]).split('/')
                                subnet, mask = subnet[0], int(subnet[1])
                        else:
                            try:
                                if len(str(row[4])) > 15:
                                    subnet = str(row[4]).split('\n')[0] #Bug fig, if a couple value in row
                                else:
                                    subnet = str(row[4])
                            except ValueError:
                                subnet = 0


                            try:
                                if len(str(row[5])) > 4:
                                    mask = str(row[5]).split('\n')[0] #Bug fig, if a couple value in row
                                    mask = int(round(float(mask)))
                                else:
                                    mask = int(round(float(row[5]))) or 0
                            except ValueError:
                                mask = 0

                        vlan_info, _ = Vlans.objects.get_or_create(
                        name=str(row[1]),
                        location=str(row[2]),
                        vlan=vlan,
                        subnet=subnet,
                        mask=mask,
                        )
                        internal_count += 1
                        try:
                            for xtag in range(6,8,1):
                                if row[xtag] != '':
                                            tag_info, _ = Tags.objects.get_or_create(name=str(row[xtag]).rstrip())
                                            vlan_info.tags.add(tag_info)
                                            internal_count += 1
                        except:
                            pass

        return internal_count