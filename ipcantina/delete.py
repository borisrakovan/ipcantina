import xlrd
from app import db
import re
from app.models import User, Company


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if str(table) in ['meal', 'order']:
            print('Clear table %s' % table)
            session.execute(table.delete())
    session.commit()


def upload_companies():
    wb = xlrd.open_workbook("C:\\Users\\brako\\Desktop\\Work\\PERGAMON\\cantina_registracia_kod.xlsx")
    sheet = wb.sheet_by_index(0) # must be 0

    for i in range(1, sheet.nrows):
        full_title = sheet.cell_value(i, 0)
        title = re.sub("([,]? spol[.,]?)", "", full_title.strip())
        title = re.sub(",?\ss\.?\s?r\.\s?o\.", "", title)

        CRN = sheet.cell_value(i, 1)
        building = sheet.cell_value(i, 2).strip()
        token = sheet.cell_value(i, 3).strip()

        c = Company(full_title=full_title, title=title, CRN=CRN, building=building, token=token)
        db.session.add(c)
    db.session.commit()

if __name__ == '__main__':
    # pass
    clear_data(db.session)
