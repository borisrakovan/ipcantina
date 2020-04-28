import xlrd
from app import db
import re
from app.models import User, Company, UserRole


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if str(table) in ['meal', 'order']:
            print('Clear table %s' % table)
            session.execute(table.delete())
    session.commit()


def upload_companies():
    wb = xlrd.open_workbook("C:\\Users\\brako\\Desktop\\Work\\pergamon\\ip\\ipcantina\\files\\cantina_registracia_kod.xlsx")
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


def create_admin():
    c = Company.query.filter(Company.title == 'Iná').first()
    u = User(first_name="Boris", surname="Rakovan", email="b.rakovan@gmail.com", phone="0911710322", company=c)
    # u = User(first_name="Pavol", surname="Skoda", email="p.skoda@ipdevelopment.sk", phone="0905610021", company=c)
    u.set_password("hesloheslo")
    u.set_urole(UserRole.ADMIN)

    db.session.add(u)
    db.session.commit()


if __name__ == '__main__':
    # clear_data(db.session)
    # c = Company(full_title='Iná', title='Iná', CRN=12345678, building='ABX', token='ABX1234')
    # db.session.add(c)
    # db.session.commit()
    # create_admin()
    # upload_companies()
    pass
