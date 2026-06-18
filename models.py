from flask_sqlalchemy import SQLAlchemy
import datetime
from bs4 import BeautifulSoup


database = SQLAlchemy()


class Item(database.Model):

    def _convert_date():
        parts = self.open_date.split("-")
        return datetime.datetime(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]), hour=0, minute=0, second=0, microsecond=0)


    def _get_time():
        return datetime.datetime.now()


    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(25), nullable=False)
    description = database.Column(database.String(100), nullable=False)
    opened = database.Column(database.Boolean, default=False)
    open_date = database.Column(database.Date, onupdate=_get_time)
    after_open = database.Column(database.Integer, default=3)

    

    def __repr__(self):
        return f"{self.name} : Opened: {self.opened}"
