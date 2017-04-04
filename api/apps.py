from django.apps import AppConfig
from api.utils import change_api_updated_at
from django.db.models.signals import post_delete, post_save


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # auth.User signals
        post_save.connect(receiver=change_api_updated_at, sender='auth.User', dispatch_uid='F8423A12-676D-4111-BCF2-809F1DAB8C25')
        post_delete.connect(receiver=change_api_updated_at, sender='auth.User' dispatch_uid='A7517433-72FE-4250-AB61-7DE2242C31C9')

        # tourpoint.TourPoint signals
        post_save.connect(receiver=change_api_updated_at, sender='tourpoint.TourPoint', dispatch_uid='3F4CF5F2-E961-4822-9D6B-A03E46864B59')
        post_delete.connect(receiver=change_api_updated_at, sender='tourpoint.TourPoint', dispatch_uid='462BCF38-3C0E-4071-BD2C-64286A1F4AD5')