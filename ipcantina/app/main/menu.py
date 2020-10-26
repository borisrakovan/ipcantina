import xlrd
import json
from datetime import timedelta
from flask import current_app

from db.models import Meal
from db.utils import DateUtils

from app.main.persist import load_settings

closed_tags = ['sviatok', 'zatvorené', 'zatvorene', 'prázdniny', 'prazdniny', 'closed', 'dovolenka']


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
                menu[weekday] = dict()
                menu[weekday]['soup'] = soup
                menu[weekday]['meals'] = meals
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
        default_prices = load_settings()["instructions"]
        for row in range(sheet.nrows):
            closed = False
            for col in range(sheet.ncols):
                if str(sheet.cell_value(row, col)).lower().strip() in closed_tags:
                    menu[day]['open'] = False
                    print("closed")
                    closed = True
                    day += 1
                    break
            if closed: continue
            print("got here")
            print(sheet.nrows)
            if sheet.cell_value(row, 0).strip() == 'A':
                menu[day]['open'] = True
                soup = sheet.cell_value(row-1, 2).strip()
                # if not soup:
                #     raise RuntimeError("Chýbajúca polievka.")

                if soup: #  might be missing
                    portion = str(sheet.cell_value(row - 1, 1)).strip()
                    cell = sheet.cell_value(row - 1, 3)
                    if isinstance(cell, float):
                        cell = int(cell)
                    allergens = str(cell).strip()
                    menu[day]['soup'] = {'portion': portion, 'description': soup, 'allergens': allergens}
                menu[day]['meals'] = []

                for i in range(row, row+3):
                    label = sheet.cell_value(i, 0).strip()
                    if label not in ['A', 'B', 'C']:
                        raise RuntimeError("Chýbajúce hlavné jedlo.")
                    portion = str(sheet.cell_value(i, 1)).strip()
                    desc = sheet.cell_value(i, 2).strip()
                    cell = sheet.cell_value(i, 3)
                    if isinstance(cell, float):
                        cell = int(cell)
                    allergens = str(cell).strip()
                    if not desc:
                        raise RuntimeError("Chýbajúce hlavné jedlo.")
                    try:
                        price = str(sheet.cell_value(i, 4)).replace('€', '').replace(',', '.').strip()
                        price = float(price) - 0.3 # ONLINE DISCOUNT
                        # price = float()
                    except Exception:
                        price = default_prices[label] - 0.3

                    menu[day]['meals'].append({"label": label, "portion": portion,
                                               "description": desc, "allergens": allergens, "price": price})
                row += 3
                day += 1
        if day < 5:
            raise RuntimeError("Chýbajúce menu pre aspoň jeden deň v týždni.")

        with open(out_path, "w", encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=False, indent=4)
