import os
import sys

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moodle.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
