# NMME

# Setup SECRET_KEY for setting.py
Create a file called local_settings.py
Inside local_settings.py create a variable called SECRET_KEY and assign a string (long, random key).

# Add in local_settings.py
FORCE_SCRIPT_NAME = '/Services'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []
