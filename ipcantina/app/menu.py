import re
import xlrd
import json
from app import app
from datetime import timedelta, datetime, time
from app.utils import DateUtils
from app.models import Meal
closed_tags = ['sviatok', 'zatvorené', 'zatvorene', 'prázdniny', 'prazdniny', 'closed', 'dovolenka']


class PriceList:
    AB_PRICE = 4.95
    C_PRICE = 4.95

    @classmethod
    def get_meal_price(cls, label):
        if label in [0, 1, 'A', 'B']:
            return cls.AB_PRICE
        elif label in [2, 'C']:
            return cls.C_PRICE
        raise ValueError("Invalid meal label passed")


class MenuUtils:

    @staticmethod
    def load_from_db():
        monday = DateUtils.affected_week_monday()
        menu = [None]*5
        uploaded = False
        for weekday in range(5):
            date = monday + timedelta(days=weekday)
            soup = Meal.query.filter(Meal.date == date, Meal.label == 'S').first()
            meals = Meal.query.filter(Meal.date == date, Meal.label != 'S').order_by(Meal.label).all()
            if len(meals) > 0:
                menu[weekday] = {"soup": soup, "meals": meals}
                uploaded = True

        if not uploaded:
            return None
        return menu

    @staticmethod
    def label_from_int(val):
        if val == 0:
            return 'A'
        if val == 1:
            return 'B'
        if val == 2:
            return 'C'

    @staticmethod
    def from_json(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_from_excel(in_path, out_path):
        wb = xlrd.open_workbook(in_path)
        sheet = wb.sheet_by_index(0) # must be 0
        menu = [dict() for _ in range(5)]

        day = 0

        for row in range(sheet.nrows):
            for col in range(sheet.ncols):
                if str(sheet.cell_value(row, col)).lower().strip() in closed_tags:
                    menu[day]['open'] = False
                    day += 1
                    continue

            if sheet.cell_value(row, 0).strip() == 'A':
                soup = sheet.cell_value(row-1, 2).strip()
                if not soup:
                    raise RuntimeError("Chýbajúca polievka.")
                menu[day]['open'] = True
                menu[day]['soup'] = soup
                menu[day]['meals'] = []

                for i in range(row, row+3):
                    label = sheet.cell_value(i, 0).strip()
                    if label not in ['A', 'B', 'C']:
                        raise RuntimeError("Chýbajúce hlavné jedlo.")
                    g = sheet.cell_value(i, 1).strip()
                    desc = sheet.cell_value(i, 2).strip()
                    if not desc:
                        raise RuntimeError("Chýbajúce hlavné jedlo.")
                    try:
                        price = str(sheet.cell_value(i, 3)).replace('€','').replace(',','.').strip()
                        price = float(price)
                        # price = float()
                    except Exception as e:
                        price = PriceList.get_meal_price(label)

                    menu[day]['meals'].append({"label": label, "g": g, "description": desc, "price": price})
                row += 3
                day += 1

        if day < 5:
            raise RuntimeError("Chýbajúce menu pre aspoň jeden deň v týždni.")

        with open(out_path, "w", encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=False, indent=4)
