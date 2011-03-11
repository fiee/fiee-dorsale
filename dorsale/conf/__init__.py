from django.conf import settings
import dorsale_settings

for setting in dir(dorsale_settings):
    if setting == setting.upper():
        setattr(settings, setting, getattr(settings, setting, getattr(dorsale_settings, setting)))
