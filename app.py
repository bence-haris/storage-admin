from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import database, Item # type: ignore
import datetime
from sqlalchemy import create_engine
# from flask_migrate import Migrate

# New imports
from pyzbar.pyzbar import decode
from PIL import Image


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fridge.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database.init_app(app)


# migrate = Migrate(app, database)


def make_migrations():
    with app.app_context():
        database.create_all()


make_migrations()
print("Created")



# DUMMY INVENTORY
INVENTORY = {
    "3856020277611": {"name": "Vegeta Noodles", "desc": "Chicken Taste, meal-sized snack", "after_open": 3},
    "5901234123457": {"name": "Gadget B", "qty": 7},
}



@app.route("/")
def index():
    current_time = datetime.datetime.now()
    inventory = Item.query.filter(Item.active == True).all()
    #inventory = Item.query.all()

    print(type(inventory))
    for item in inventory:
        
        if item.opened:
            opening = item.open_date
            item.after_open = opening + datetime.timedelta(item.after_open)
            print(f"CALCULATED: {item.open_date.month}")
            item.opened = "Felbontva"
            if current_time.year == opening.year and current_time.month == opening.month and current_time.day == item.after_open.day:
                item.after_open = "MA!"
            elif current_time.year >= opening.year and current_time.month >= opening.month and current_time.day > opening.day:
                item.after_open = "LEJÁRT!!!"
        else:
            item.open_date = ""
            item.after_open = f"{item.after_open} nap"
            item.opened = "Bontatlan"
    
    return render_template("index.html", inventory=inventory)


@app.route("/items")
def items(): 
    items = Item.query.all()
    return render_template("items.html", items=items)

@app.route("/scan", methods=["GET"])
def scan_item():
    return render_template("scan.html")


@app.route("/add", methods=["POST"])
def add_item():

    inventory = Item.query.all()

    item_id = request.form.get("item_id")
    item_name = request.form.get("item_name")
    item_desc = request.form.get("item_desc")
    item_after_open = request.form.get("item_after_open")
    item_opened = request.form.get("item_opened")
    item_active = request.form.get("item_active")

    for item in inventory:
        if item.name == item_name:
            item_id = item.id


    if item_opened == "":
        item_opened_converted = None
        opened = False
    else:
        parts = item_opened.split("-")
        item_opened_converted = datetime.datetime(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]), hour=0, minute=0, second=0, microsecond=0)
        opened = True

    if item_active:
        item_active = True
    else:
        item_active = False

    print(f"AT TIME: {item_opened}")

    new_item = Item(id=item_id, name=item_name, description=item_desc, after_open=item_after_open,open_date=item_opened_converted, opened=opened, active=item_active)

    database.session.add(new_item)
    database.session.commit()

    return redirect(url_for('index'))

@app.route("/delete/<int:item_id>", methods=["GET"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    database.session.delete(item)
    database.session.commit()

    return redirect(url_for('items'))

@app.route("/deactivate/<int:item_id>", methods=["GET"])
def deactivate_item(item_id):
    item = Item.query.get(item_id)
    item.opened = False
    item.active = False
    database.session.commit()

    return redirect(url_for('index'))

@app.route("/open/<int:item_id>", methods=["GET"])
def open_item(item_id):
    item = Item.query.get(item_id)
    item.opened = True
    database.session.commit()

    return redirect(url_for('index'))

@app.route("/activate/<int:item_id>", methods=["GET"])
def activate_item(item_id):
    item = Item.query.get(item_id)
    item.opened = False
    item.active = True
    database.session.commit()

    return redirect(url_for('index'))

@app.route("/api/scan", methods=["POST"])
def push_scan():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    try:
        img = Image.open(request.files["image"].stream)
    except Exception:
        return jsonify({"error": "Could not read image"}), 400

    #img.convert("RGB").save("last_frame.jpg")


    results = decode(img)

    if not results:
        return jsonify({"found": False, "barcode": None})
    

    # Take the first barcode found in the frame
    symbol = results[0]
    code = symbol.data.decode("utf-8")

    inventory = Item.query.all()

    for item in inventory:
        # Item already present in the inventory
        if item.id == int(code):
            print(item)
            
            selected_item = Item.query.get(item.id)
            selected_item.active = True
            database.session.commit()

            return jsonify({
                "found": True,
                "barcode": code,
                "type": symbol.type,
                "item": {"name": item.name, "qty": item.description},
            })
        #item = INVENTORY.get(code)

    #if item:
    #    new_item = Item(name=item["name"], description=item["desc"], after_open=item["after_open"],open_date=None, opened=False)
    #    database.session.add(new_item)
    #    database.session.commit()

    return jsonify({
        "found": False,
        "barcode": code,
        "type": symbol.type,
        "item": {"name": "Unknown", "qty": "No Description"},
    })

if __name__ == '__main__':
    app.run("0.0.0.0")
