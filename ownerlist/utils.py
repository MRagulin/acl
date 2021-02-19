import os
from pathlib import Path
from django.core.files.storage import FileSystemStorage
from django.apps import apps
import socket
import re
import xlrd
from django.conf import settings
from django.db.utils import IntegrityError, DataError
import datetime
import time
import asyncio
from docx import Document
from docx.shared import Pt
import uuid

FUN_SPEED = 0

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

def count_perf(f):
    """Декоратор для измерения скорости поиска"""
    def wraper(*args, **kwargs):
        global FUN_SPEED
        time_init = datetime.datetime.now()
        result = f(*args, **kwargs)
        time_end = datetime.datetime.now()
        total = time_end - time_init
        FUN_SPEED = total
        #print('Time: {}'.format(total))
        return result
    return wraper

@count_perf
def DeepSearch(string: str = ''):
    result = ''
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", string):
        Iplist = apps.get_model('ownerlist', 'Iplist')
        result = Iplist.objects.filter(ipv4=string)
        if not result:
            result = Iplist.objects.filter(ipv4__contains=string)[:5]
        #result = Iplist.objects.filter(ipv4__contains=string)[:5]
    #time.sleep(5)
    return result



def write_history(request, string, status) -> None:
    """Сохранять историю поиска, для улучшения качества поиска"""
    hc = apps.get_model('ownerlist', 'HistoryCall')
    ip = apps.get_model('ownerlist', 'Iplist')

    ip_object, obj = ip.objects.get_or_create(ipv4=request.META.get('REMOTE_ADDR'))
    hc_object, obj = hc.objects.get_or_create(string=string,
                                         ipv4=ip_object,
                                         status=status)


def search_text(request=None, string: str = '') -> dict:
    """ Функция для поиска данных в БД"""
    global FUN_SPEED
    result = DeepSearch(string)
    context = {'SearchFor': string}
    context['Data'] = result
    context['TakeTime'] = FUN_SPEED
    context['Info'] = ''
    FUN_SPEED = 0
    write_history(request, string, bool(result))
    return context


# def ExcelHandler(filename = ''):
#     ext = filename.split(".")[-1].lower()
#     print(ext)
#     if ext == 'xls': #old format
#         return ExtractDataXls(filename)
#     else:
#         if ext == 'xlsx': #new format
#             from openpyxl import load_workbook
#             print('Open File: {}'.format(filename))
#             wb = load_workbook(filename)
#             print("Sheets: {}".format(wb.get_sheet_names()))
#         else:
#             print('File not supported :(')
#
# def is_row_empty(row):
#     result = True
#     for d in row:
#         if d != '':
#             result = False
#             break
#     return result
#
# def gethostname(ip):
#     result = socket.gethostbyaddr(ip)
#     if len(result) > 1:
#         return result[0]
#     else:
#         return ''
#
# def isvalidip(ip, page_name = ''):
#     l = len(str(ip));
#     if (l ==0) or (l > 15): return False
#     s = str(ip).split('.')
#     if len(s) >= 3:
#         return True
#     else:
#         return False
#
#
# def get_ip_from_page(page):
#     try:
#         ip = re.findall(r"(\d{1,3})", page)
#         return ".".join(page)
#     except:
#         pass
#     return ""





class ExtractDataXls():
    """Основной класс для анализа xls файла"""
    def __init__(self, filename=''):
        self.ip_addr_idx = 1
        self.count_total: int = 0 #total records in db
        self.error_count: int = 0 #total errors
        self.rb = xlrd.open_workbook(filename, formatting_info=True)
        self.current_page = None
        self.sheet_tags = self.rb.sheet_names()
        self.Vlans = apps.get_model('ownerlist', 'Vlans')
        self.Tags = apps.get_model('ownerlist', 'Tags')
        self.Iplist = apps.get_model('ownerlist', 'Iplist')
        self.Owners = apps.get_model('ownerlist', 'Owners')
        self.page_headers = ['ответственный', 'комменты', 'ip address', 'Имя сервера','отвеcтвенный', 'nat inside']
        self.fio_exclude_list = ['гусев','оксенюк','северцев','егоров','совинский','огнивцев','допиро','мюлекер','уволен','иренов','казаков','куслеев']



    def execute_file_parsing(self):
        """Выбираем парсер на основе имени страницы"""
        result = 0
        for self.sheet_tag in self.sheet_tags:
            self.current_page = self.rb.sheet_by_name(self.sheet_tag)
            if self.current_page.nrows == 0:  # Count row
                if settings.DEBUG:
                    print("Страница {} пустая, пропущено...".format(self.current_page))
                    return 0
            # else:
            #     if settings.DEBUG:
            #         print('Извлекаем данные из: {} ...'.format(self.sheet_tag))
            #         print('*'*60)
            if self.sheet_tag == 'VLAN DESCRIPTION':
                    result += self.ExtractVlanInfo()
            elif self.sheet_tag == 'VLAN_CORE_ACI':
                    result += self.ExtractVlanInfo(name_idx=6, location_idx=3, vlan_idx=2, subnet_idx=4, mask_idx=5, tag1_idx=7, tag2_idx=8)
            elif self.sheet_tag == '10.255.10.0 (NGNX-Serv)':
                result += self.ExtractIPInfo(domain_idx=0, ip_idx=1, owner_idx=2, comment_idx=3)
            elif self.sheet_tag == '213.33.175.0 _24':
                result += self.ExtractIPInfo(domain_idx=1, ip_idx=2, owner_idx=4, comment_idx=5)
            elif self.sheet_tag == 'активка 172.16.82.X':
                result += self.ExtractIPInfo(domain_idx=1, ip_idx=0, owner_idx=2, comment_idx=3)
            elif self.sheet_tag == '195.239.64.хх':
                result += self.ExtractIPInfo(domain_idx=0, ip_idx=1, owner_idx=3, comment_idx=4)
            elif self.current_page.ncols == 4:
                    result += self.ExtractIPInfo()
            else:
                if settings.DEBUG:
                        print("Страница содержит другое количество колонок <> 4, {} анализируем...".format(self.current_page.ncols))
                result += self.PageStructAnalyzer(self.current_page)
        return result


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
            return ""


    def isvalidip(self, ip)-> bool:
        l = len(str(ip))
        if (l == 0) or (l > 15): return False
        s = str(ip).split('.')
        if len(s) >= 3:
            return True
        else:
            return False

    def ExtractVlanInfo(self, name_idx=1, location_idx=2, vlan_idx=3, subnet_idx=4, mask_idx=5, tag1_idx=6, tag2_idx=7)->int:
        """Парсер страницы с описанием VLAN"""
        row_index: int = 0
        tags: list = []
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

                        vlan_info, _ = self.Vlans.objects.get_or_create(
                        name=str(row[name_idx]),
                        location=str(row[location_idx]),
                        vlan=vlan,
                        subnet=subnet,
                        mask=mask,
                        )
                        # if created obj
                        if _:
                                self.count_total += 1

                        try:
                            tags.append(self.sheet_tag)
                            tags.append(row[tag1_idx])
                            tags.append(row[tag2_idx])

                            for tag in tags:
                                if (tag != '') and len(tag) > 1:
                                            if len(str(tag).split('.')) >= 3:  # If tag as Gateway's IP
                                                tag = "Gateway: {}".format(tag)
                                            tag_info, _ = self.Tags.objects.get_or_create(name=str(tag).rstrip())
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

    def ExtractIPInfo(self, domain_idx=0, ip_idx=1, owner_idx=2, comment_idx=3, stop_recurse = False, HasTags=[])->int:
        tags: list = []
        self.error_count = 0
        Header_POS = 0
        created = None

        ip_addr = ''
        domain = ''
        owner = ''
        comment = ''



        # if HasTags is not None:
        #     if len(HasTags) > 0:
        #         tags = HasTags

        #print(self.sheet_tag)
        #return 0
        self.count_total = 0
        for row_idx in range(self.current_page.nrows):
            row = self.current_page.row_values(row_idx)
            if not self.is_row_empty(row):
                # if self.sheet_tag == 'Орел':
                #     print ('')
                if len(row) >= 3:
                    if row_idx in range(0, 3):
                        if row[row_idx] in self.page_headers: #Пропускаем заголовки
                            Header_POS = row_idx
                            continue
                if self.isvalidip(row[ip_idx]):
                    ip_addr = row[ip_idx]
                elif len(str(row[ip_idx])) <= 5: #15.0
                            try:
                                tmp = int(round(float(row[ip_idx]))) or 0
                            except ValueError:
                                tmp = 0
                                continue
                            else:
                                if tmp > 0:
                                    ip_addr = self.get_ip_from_page(str(self.sheet_tag))
                                    if ip_addr != '':
                                            ip_addr = ip_addr + '.' + str(tmp)
                else:
                    self.error_count += 1
                    if self.error_count >= 5:
                        if not stop_recurse:
                            if settings.DEBUG:
                                print("Много ошибок на странице, провёдем анализ страницы ...")
                            self.PageStructAnalyzer(self.current_page)
                        else:
                            if settings.DEBUG:
                                print("********************Ошибка при анализе странице {}****************".format(self.sheet_tag))
                        return 0
                    continue
                try:
                    if domain_idx is not None:
                        domain = row[domain_idx]
                except:
                    domain = ''


                try:
                    if owner_idx is not None:
                        owner = row[owner_idx]
                except:
                    owner = ''

                try:
                    if comment_idx is not None:
                        comment = row[comment_idx]
                except:
                    comment = ''

                if len(HasTags) > 0:
                    for tag in HasTags:
                        try:
                            tmp = row[int(tag)]
                            if tmp != '':
                                name = self.current_page.cell_value(Header_POS, int(tag))
                                if name != '':
                                    tmp = name + ":"+tmp
                                if tmp not in tags:
                                    tags.append(tmp)
                        except:
                            pass
                if self.sheet_tag not in tags:
                    tags.append(self.sheet_tag)

#-----------------------------------------------------------------------------------------------------------------------
                try:
                    if comment and re.match(r"([а-яА-Я\.\s()]){5,}", str(comment)):
                        tmp = comment.lower().strip()
                        exists = list(filter(lambda s: s in tmp, self.fio_exclude_list))
                        #exists = any(substring in string for string in strings)
                        #if comment.lower() in self.fio_exclude_list:
                        if len(exists) > 0:
                            owner, comment = comment, owner
                except:
                    pass
#-----------------------------------------------------------------------------------------------------------------------

                try:
                    if owner:
                        if owner.find('://') != -1:
                            owner, comment = comment, owner
                except:
                    pass

                if ip_addr != '':
                   # if not self.isvalidip(ip_addr):

                       # continue
                    # if comment_idx != -1:
                    #     print("{} {} {} {} ".format(domain, ip_addr, row[owner_idx], row[comment_idx]))
                    # else:
                    if (owner == '') or len(owner) <= 1:
                        owner_info = None
                    else:
                        #try:
                            owner_info, created = self.Owners.objects.get_or_create(username = owner)
                        #except:
                            #owner_info = self.Owners.get_default_owner()

                    try:
                        ip_info, created  = self.Iplist.objects.get_or_create(
                            ipv4 = ip_addr,
                            hostname = domain,
                            owner = owner_info,
                            comment = comment
                        )
                    except IntegrityError:
                        ip_info = self.Iplist.objects.get(ipv4=ip_addr)
                        ip_info.ipv4 = ip_addr
                        ip_info.hostname = domain
                        ip_info.owner = owner_info
                        ip_info.comment = comment
                        ip_info.save()

                    except DataError:
                        print("- Ошибка данных: {} на странице: {}".format(ip_addr, self.sheet_tag))
                        continue

                    if created:
                        self.count_total += 1


                    try:
                        for tag in tags:
                            if (tag != '') and len(tag) > 1:
                                tag_info, created = self.Tags.objects.get_or_create(name=str(tag).rstrip())
                                if tag_info not in ip_info.tags.all():
                                    ip_info.tags.add(tag_info)
                    except:
                        pass

                    finally:
                            #print("{} {} {} {}-> {}".format(domain, ip_addr, owner, comment, " [" + ' '.join(tags) + "]"))

                            tags.clear()
        if settings.DEBUG:
            print("Страница: {} записано: {}".format(self.sheet_tag, self.count_total))
        return self.count_total

    def PageStructAnalyzer(self, page, DEBUG = False)-> None:
        """Написанный на коленке анализатор данных на странице в xls"""
        is_domain = 0
        is_ip = 0
        is_owner = 0
        is_comment = 0
        is_add = 0
        col_index ={}
        #RowIndex = 0
        #RowBlackListByNumber = []
        skip_domain = False
        skip_owner = False
        skip_ip = False
        skip_commnet = False

        col_index['domain'] = None
        col_index['ip'] = None
        col_index['owner'] = None
        col_index['comment'] = None

        Tags = []
        #col_index = {}
        # if self.sheet_tag == '172.16.88.Х Avaya':
        #     print('')
        if not (page.ncols > 0):  # and page.ncols < 6
                print("Page {} has been skipped, unknown amount col {}".format(self.sheet_tag, page.ncols))
        else:
                for idx_col in range(page.ncols):
                    col_stat = {'Unknown': 0,
                                'is_domain': 0,
                                'is_ip': 0,
                                'is_owner': 0,
                                'is_comment': 0,
                                'is_tag': 0}

                    #RowIndex = 0
                    if idx_col >=8: #Skip comment in tables
                        continue

                    for index, col in enumerate(page.col_values(idx_col)):
                        if col == '':
                            continue
                        if index in range(0, 2):
                            if col in self.page_headers:
                                continue
                        try:
                            if len(str(col)) <= 1:
                                continue
                            if (re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", str(col)) or
                                re.match(r"^(\d+.\d)|(\d)$", str(col))):
                                    if skip_ip == False:
                                        col_stat['is_ip'] += 1
                                        continue
                                    else:
                                      if  idx_col not in Tags:
                                            Tags.append(idx_col)
                                      continue
                        except TypeError:
                            pass


                        try:
                            if (skip_domain == False) and re.match(r"([a-zA-Z0-9\-\.\\()\_]){4,}", str(col)):  # [А-я]+
                                    col_stat['is_domain'] += 1
                                    continue
                        except TypeError:
                                pass


                        try:
                            if (skip_owner == False) and re.match(r"([а-яА-Я\.\s()]){5,}", str(col)):
                                   col_stat['is_owner'] += 1
                                   continue
                        except:
                            pass

                                #else:
                        if len(str(col)) > 3:
                                        t = str(col).lower().find('vlan')
                                        if t > 0: pass
                                        #     str_sum = len(col)
                                        #     #col_stat['is_tag'] += 1
                                        #     try:
                                        #         #cut_vlan = col.split(' ')
                                        #         if idx_col not in Tags:
                                        #             Tags.append(idx_col)
                                        #             continue
                                        #     except:
                                        #         pass
                                            # in ['vlan', 'vlan name', 'location', ]
                                        else:
                                            if skip_commnet == False:
                                                col_stat['is_comment'] += 1
                                            else:
                                                if idx_col not in Tags:
                                                    Tags.append(idx_col)
                                                    continue





                    max_v = max(col_stat, key=col_stat.get)
                    if 'Unknown' == max_v:
                        continue
                    elif max_v == 'is_domain':
                        col_index['domain'] = idx_col
                        skip_domain = True
                        if idx_col in Tags:
                            Tags.remove(idx_col)
                    elif  max_v == 'is_owner':
                            skip_owner = True
                            col_index['owner'] = idx_col
                            if idx_col in Tags:
                                Tags.remove(idx_col)
                    elif max_v == 'is_ip':
                                skip_ip = True
                                col_index['ip'] = idx_col
                                if idx_col in Tags:
                                    Tags.remove(idx_col)
                    elif not skip_commnet:
                            col_index['comment'] = idx_col
                            if idx_col in Tags:
                                Tags.remove(idx_col)

                    if max_v == 'is_comment':
                                    if idx_col == 2:
                                            if (col_stat['is_owner']) >= 5:
                                                col_index['owner'] = idx_col
                                                if idx_col in Tags:
                                                    Tags.remove(idx_col)
                                                if settings.DEBUG:
                                                    print(
                                                        "Page: {}| Col {}| possible: [FIX] owner (d:{},i:{}, o:{},c:{},t:{})".format(
                                                            self.sheet_tag, idx_col, col_stat['is_domain'],
                                                            col_stat['is_ip'],
                                                            col_stat['is_owner'], col_stat['is_comment'], col_stat['is_tag']))
                                                continue
                                    else:
                                        skip_commnet = True


                        #print("Page: {}| Col {}| possible empty, skipped".format(self.sheet_tag, idx_col))
                    #else:
                    if DEBUG:
                        print("Page: {}| Col {}| possible: {}(d:{},i:{}, o:{},c:{},t:{})".format(self.sheet_tag, idx_col,
                                                                                                max_v,
                                                                                                col_stat['is_domain'],
                                                                                                col_stat['is_ip'],
                                                                                                col_stat['is_owner'],
                                                                                                col_stat['is_comment'],
                                                                                                col_stat['is_tag']))

        if not DEBUG:
            return self.ExtractIPInfo(domain_idx=col_index['domain'], ip_idx=col_index['ip'], owner_idx=col_index['owner'],
                                  comment_idx=col_index['comment'], stop_recurse=True, HasTags=Tags)


def make_doc(data_set={}):
    TEMPLATE_FILE = os.path.join(BASE_DIR, 'templates\\ACL.docx')
    APP_FILE = 'static\\docx\\Application_' + str(uuid.uuid4()) + '.docx'
    doc = Document(TEMPLATE_FILE)
    doc.styles['Normal'].font.name = 'Verdana'
    doc.styles['Normal'].font.size = Pt(10)

    for data_inx, data in enumerate(data_set):
        table_tmp = doc.tables[data_inx]  # Берем таблицу
        if data_inx == 0:  # Для таблицы контакты, меняем правила игры
            for row_idx, row_data in enumerate(data_set[data]):
                table_tmp.cell(row_idx, 1).text = row_data
        else:
            for key, value in enumerate(data_set[data], start=1):
                for cell_idx, cell_val in enumerate(value):
                    table_tmp.cell(key, cell_idx).text = cell_val

    doc.save(os.path.join(BASE_DIR, APP_FILE))
    return "..\\..\\" + APP_FILE
