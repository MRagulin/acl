import os
import sys
from django.core.wsgi import get_wsgi_application
sys.path.append('/var/www/acladmin')
sys.path.append('/var/www/acladmin/acladmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acladmin.settings')
application = get_wsgi_application()
