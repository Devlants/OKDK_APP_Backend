from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from order.models import Favorite
from .models import Brand
import requests

def updateMenu(brand):
    new_data = []
    favorites = Favorite.objects.all()

    api = brand.api + "menu/list/"
    response = requests.get(api).json()
    for data in response:
        new_data += [item["id"] for item in data["menues"]]

    for favorite in favorites:
        if favorite.menu not in new_data:
            favorite.delete()

def updateTemperature(brand):
    new_data = []
    favorites = Favorite.objects.all()

    api = brand.api + "order/temperature/list/"
    response = requests.get(api).json()
    for data in response:
        new_data.append(data["id"])

    for favorite in favorites:
        if favorite.temperature not in new_data:
            favorite.delete()

def updateSize(brand):
    new_data = []
    favorites = Favorite.objects.all()

    api = brand.api + "order/size/list/"
    response = requests.get(api).json()
    for data in response:
        new_data.append(data["id"])

    for favorite in favorites:
        if favorite.size not in new_data:
            favorite.delete()

def updateBrand():
    brands = Brand.objects.all()

    for brand in brands:
        updateMenu(brand)
        updateTemperature(brand)
        updateSize(brand)

def start():
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job(trigger=CronTrigger(hour='0', minute='0', second='0'), id='update_menu')
    # @scheduler.scheduled_job(trigger=CronTrigger(second='*/10'), id='update_menu')
    def auto_check():
        updateBrand()

    scheduler.start()
