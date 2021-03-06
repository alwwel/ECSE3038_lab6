from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import Schema, ValidationError, fields
from flask_pymongo import PyMongo
from json import loads
from datetime import datetime
from bson.json_util import dumps
import os



app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = os.getenv("MONGO_CONNECTION_STRING")
mongo = PyMongo(app)

class TankSchema(Schema):
    location = fields.String(required=True)
    longitude = fields.Float(required=True)
    latitude= fields.Float(required=True)
    percentage_full = fields.Integer(required=True)
    

@app.route("/data", methods=["GET"])
def get_data():
    Tanks = mongo.db.tanks.find()
    Tank_list = loads(dumps(Tanks))

    return jsonify(Tank_list)

@app.route("/data", methods=["POST"])
def new_entry():
    request_dict = request.json 
    try: 
        new_tank = TankSchema().load(request_dict)
    except ValidationError as error:
        return(error.messages, 400)
    
    tank_doc = mongo.db.tanks.insert_one(new_tank)
    tank_id = tank_doc.inserted

    tank = mongo.db.tanks.find_one({"_id": tank_id})
    tank_json = loads(dumps(tank))
    return jsonify(tank_json)

@app.route("/data/<ObjectId:id>", methods=["PATCH"])
def update(id):
    request_dict = request.json 

    try: 
        TankSchema(partial=True).load(request_dict)
    except ValidationError as error:
        return(error.messages, 400)

    mongo.db.tanks.update_one({"_id": id}, {"$set": request.json})
    tank = mongo.db.tanks.find_one(id)
    tank_json = loads(dumps(tank)) 
    return jsonify(tank_json)

class Level(Schema):
	tank_id = fields.String(required=True)
	water_Level=fields.Integer(required=True)

@app.route("/tankpos",methods=["POST"])
def stat():
    bulbstatus = False
    request_dict = request.json 
    try: 
        new_tank = Level().load(request_dict)
    except ValidationError as error:
        return(error.messages, 400)
    
    tank_document = mongo.db.levels.insert_one(new_tank)
    tank_id = tank_document.inserted_id
    tank = mongo.db.levels.find_one({"_id": tank_id})
    tank_json = loads(dumps(tank))
    if tank_json["water_Level"] in range(60,100):
        bulbstatus=True
    responeobj={
	"bulb": bulbstatus,
	"message": "confirmed data storage",
	"date": str(datetime.now()),
    }
    return jsonify(responeobj)

@app.route("/data/<ObjectId:id>", methods=["DELETE"])
def delete(id):      
    tank = mongo.db.tanks.delete_one({"_id": id})

    if tank.deleted == 1:
        return { "success": True }
    return { "success": False }, 404


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port="5000")
