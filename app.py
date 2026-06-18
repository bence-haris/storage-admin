from flask import Flask, render_template, request, redirect, url_for
from models import database, Item # type: ignore
import datetime
# from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fridge.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database.init_app(app)


# migrate = Migrate(app, database)


def make_migrations():
    with app.app_context():
        database.create_all()


#make_migrations()
print("HI")

@app.route("/")
def index():
    current_time = datetime.datetime.now()
    inventory = Item.query.all()
    for item in inventory:
        
        if item.opened:
            opening = item.open_date
            item.after_open = opening + datetime.timedelta(item.after_open)
            item.opened = "Felbontva"
            if current_time.year == opening.year and current_time.month == opening.month and current_time.day == item.after_open.day:
                item.after_open = "MA!"
            elif current_time.year >= opening.year and current_time.month >= opening.month and current_time.day > item.after_open.day:
                item.after_open = "LEJÁRT!!!"
        else:
            item.open_date = ""
            item.after_open = f"{item.after_open} nap"
            item.opened = "Bontatlan"
    
    return render_template("index.html", inventory=inventory)

@app.route("/add", methods=["POST"])
def add_item():
    item_name = request.form.get("item_name")
    item_desc = request.form.get("item_desc")
    item_after_open = request.form.get("item_after_open")
    item_opened = request.form.get("item_opened")

    if item_opened == "":
        item_opened_converted = None
        opened = False
    else:
        parts = item_opened.split("-")
        item_opened_converted = datetime.datetime(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]), hour=0, minute=0, second=0, microsecond=0)
        opened = True

    print(f"AT TIME: {item_opened}")

    new_item = Item(name=item_name, description=item_desc, after_open=item_after_open,open_date=item_opened_converted, opened=opened)

    database.session.add(new_item)
    database.session.commit()

    return redirect(url_for('index'))

@app.route("/delete/<int:item_id>", methods=["GET"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    database.session.delete(item)
    database.session.commit()

    return redirect(url_for('index'))

@app.route("/open/<int:item_id>", methods=["GET"])
def open_item(item_id):
    item = Item.query.get(item_id)
    item.opened = True
    database.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run("0.0.0.0")
