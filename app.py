from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://shannifyme:rD4wldnKDZpxLO2a@cluster0.pc9px01.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number =number.replace("whatsapp:","")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Hi, thanks for contacting *Yingity's Shop*.\nYou can choose from one of the options below: "
                          "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* ice cream \n 3️⃣ To know our *working hours* \n 4️⃣ "
                          "To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message("You can contact us through phone or email. \n\n*Phone*: 9180 5000 \n*Email*: yingity@gmail.com")
        elif option == 2:
            res.message("You have entered *ordering mode*.")
            users.update_one(
                {"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following ice cream flavours to order: \n\n1️⃣ Sea Salt Gula Melaka  \n2️⃣ Salted Caramel Vanilla Protein \n3️⃣ Tiramisu"
                "\n4️⃣ Mango Mania \n5️⃣ Pandan Coconut \n6️⃣ Blue Pea Vanilla \n7️⃣ Almond Biscotti \n8️⃣ Carrot Cake "
                "\n9️⃣ Double Chocolate Chip  \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work 24/7 because I'm a 🤖")
        elif option == 4:
            res.message(
                "We have multiple stores across Singapore. Our main center is in *a seaside home in Sentosa*.")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* ice cream \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address*")
        elif 1 <= option <= 9:
            cakes = ["Sea Salt Gula Melaka", "Salted Caramel Vanilla Protein", "Tiramisu",
                     "Mango Mania", "Pandan Coconut", "Blue Pea Vanilla", "Almond Biscotti", "Carrot Cake", "Double Chocolate Chip"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res.message("Please enter your address to confirm the order")
            res.message("Excellent choice 😉")

        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us 😊")
        res.message(f"Your order for *{selected}* has been received and will be delivered within an hour")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* ice cream \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})

    users.update_one({"number":number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()

