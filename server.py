#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Monkey patch for flask socketio
try:
    from eventlet import monkey_patch as monkey_patch
    monkey_patch()
except ImportError:
    try:
        from gevent.monkey import patch_all
        patch_all()
    except ImportError:
        pass

import os
import json
import datetime, time
import config
from bson.objectid import ObjectId
from bson import json_util
from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, send, emit


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)

# add mongo url to flask config, so that flask_pymongo can use it to make connection
app.config['MONGO_URI'] = config.DB
socketio = SocketIO(app)
mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template('index.html')


# USER STUFF
@app.route('/api/users', methods=['GET'])
def findAllUsers():
    users = []
    for user in mongo.db.users.find():
        users.append(user)
    return json.dumps(users, default=json_util.default)


@app.route("/api/users", methods=['POST'])
def createUser():
  userData = request.get_json(force=True)
  res = mongo.db.users.insert_one(userData)
  return json.dumps(res.inserted_id, default=json_util.default)


@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def handleUser(user_id):

  if request.method == 'GET':
    user = mongo.db.users.find_one({"_id": user_id})
    return json.dumps(user, default=json_util.default)

  if request.method == 'PUT':
    newUser = request.get_json(force=True)
    user = mongo.db.users.find_one_and_update({"_id": user_id}, {"$set": newUser})
    return json.dumps(user, default=json_util.default)

  if request.method == 'DELETE':
    res = mongo.db.users.delete_one({"_id": user_id})
    return json.dumps(res, default=json_util.default)


# ITEM STUFF
@app.route("/api/items", methods=['GET'])
def findAllItems():
    items = []
    # TODO: Check if time period has ended. If true, move item to last bidder's cart with type "bid" and mark not active
    for item in mongo.db.items.find():
        items.append(item)
    return json.dumps(items, default=json_util.default)

@app.route("/api/items", methods=['POST'])
def createItem():
    itemData = request.get_json(force=True)
    mongo.db.items.insert_one(itemData)
    # TODO: append _id.$oid into itemData.seller's listings
    return json.dumps(itemData, default=json_util.default)

@app.route("/api/items/<item_id>", methods=['GET', 'PUT', 'DELETE'])
def handleItem(item_id):
    if request.method == 'GET':
        itemData = mongo.db.items.find_one_or_404({"_id": ObjectId(item_id)})
        return json.dumps(itemData, default=json_util.default)

    if request.method == 'PUT':
      newItem = request.get_json(force=True)
      item = mongo.db.items.find_one_and_update({"_id": ObjectId(item_id)}, {"$set": newItem})
      return json.dumps(item, default=json_util.default)

    if request.method == 'DELETE':
        res = mongo.db.items.delete_one({"_id": ObjectId(item_id)})
        return json.dumps(res, default=json_util.default)


# BID STUFF
@app.route('/api/items/<item_id>/bid', methods=['POST'])
def bid(item_id):
    new_bid = request.get_json(force=True)
    item = mongo.db.items.find_one({"_id": ObjectId(item_id)})
    # TODO: Store bid in user's bid history
    # Append {bidAmount, _id, timestamp}
    if "bid_history" not in item:
        item["bid_history"] = [new_bid]
    else:
        item["bid_history"].append(new_bid)
    mongo.db.items.find_one_and_update({"_id": ObjectId(item_id)}, {"$set": item})
    return json.dumps(new_bid, default=json_util.default)


# CART STUFF
# TODO: Add edit functionality if it was buyNow type
@app.route('/api/users/<user_id>/cart', methods=['GET', 'POST'])
def cart(user_id):
    if request.method == 'GET':
        cart = mongo.db.users.find_one({"_id": user_id})['cart']
        print(cart)
        return json.dumps(cart, default=json_util.default)

    elif request.method == 'POST':
        new_cart_item = request.get_json(force=True)
        user = mongo.db.users.find_one({"_id": user_id})
        if "cart" not in user:
            user["cart"] = [new_cart_item]
        else:
            user["cart"].append(new_cart_item)
        res = mongo.db.users.find_one_and_update({"_id": user_id}, {"$set": {"cart": user["cart"]}})
        return json.dumps(res, default=json_util.default)

@app.route('/api/users/<user_id>/checkout', methods=['POST'])
def checkout(user_id):
    user = mongo.db.users.find_one({"_id": user_id})
    # Store cart in buyHistory
    cart = user["cart"]
    timestamp = time.time() * 1000
    new_buy = {"timestamp" : timestamp, "items" : cart}
    if "buyHistory" not in user:
        user["buyHistory"] = [new_buy]
    else:
        user["buyHistory"].append(new_buy)

    mongo.db.users.find_one_and_update({"_id" : user_id}, {"$set" : user})

    #flag items
    for i in cart:
        item = mongo.db.items.find_one({"_id" : ObjectId(i["_id"])})
        item["soldFlag"] = True
        mongo.db.items.find_one_and_update({"_id" : ObjectId(i["_id"])}, {"$set" : item})
        # Go through all users, check if item is in their cart, if so, remove
        mongo.db.users.update({},{ "$pull": { "cart": { "_id" : i["_id"] } } }, multi= True)

    # Clear cart
    user["cart"] = []
    res = mongo.db.users.find_one_and_update({"_id": user_id}, {"$set" : user})
    return json.dumps(res, default=json_util.default)


# WATCHLIST
@app.route('/api/users/<user_id>/watchlist', methods=['GET', 'POST'])
def watchlist(user_id):
    if request.method == 'GET':
        watchlist = mongo.db.users.find_one({"_id": user_id})['watchlist']
        return json.dumps(watchlist, default=json_util.default)

    elif request.method == 'POST':
        new_watchlist_item = request.get_json(force=True)
        user = mongo.db.users.find_one({"_id": user_id})
        if "watchlist" not in user:
            user["watchlist"] = [new_watchlist_item]
        else:
            if new_watchlist_item not in user["watchlist"]: # can't add same item to watchlist again
                user["watchlist"].append(new_watchlist_item)
        res = mongo.db.users.find_one_and_update({"_id": user_id}, {"$set": {"watchlist": user["watchlist"]}})
        return json.dumps(res, default=json_util.default)

# remove an item from watchlist
@app.route('/api/users/<user_id>/watchlist/<item_id>', methods = ['DELETE'])
def delete_watchlist_item(user_id, item_id):
    watchlist = mongo.db.users.find_one({"_id": user_id})["watchlist"]
    item_id = {"_id": item_id}
    print(watchlist)
    if item_id in watchlist:
        watchlist.remove(item_id)
        res = mongo.db.users.find_one_and_update({"_id": user_id}, {"$set": {"watchlist": watchlist}})
    else:
        res = mongo.db.users.find_one({"_id": user_id}) # TODO: Why this????
    return json.dumps(res, default=json_util.default)
# TODO: This is too repetitive. Looks very much like update.
# Need to group them up.


@app.route('/api/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        categories = mongo.db.misc.find_one_or_404({"name": "categories"})
        return json.dumps(categories, default=json_util.default)

    elif request.method == 'POST':
        category = request.get_json(force=True)
        current_categories = mongo.db.misc.find_one_or_404({"name": "categories"})
        current_categories["data"].append(category)
        res = mongo.db.misc.find_one_and_update({"name": "categories"}, {"$set": {"data": current_categories["data"]}})
        return json.dumps(res, default=json_util.default)

@app.route('/api/users/<user_id>/notifications', methods=['POST'])
def notificationsRead(user_id):
    user = mongo.db.users.find_one({"_id": user_id})
    notifications = user["notifications"]
    for i in range(len(notifications)):
        notifications[i]["read"] = True
    user["notifications"] = notifications
    mongo.db.users.find_one_and_update({"_id": user_id}, {"$set": user})
    return json.dumps(notifications, default=json_util.default)

@socketio.on('bid')
def handle_bid(bid):
    print("RECEIVED BID!" + str(bid))
    #Handle bid
    new_bid = json.loads(bid)
    item_id = new_bid['itemID']
    item = mongo.db.items.find_one({"_id": ObjectId(item_id)})
    user = mongo.db.users.find_one({"_id": new_bid["userID"]})
    if len(item["bid_history"]) == 0:
        item["bid_history"] = [new_bid]
        #Store in user's bidHistory
        user["bidHistory"].append(new_bid)
        mongo.db.users.find_one_and_update({"_id": new_bid["userID"]}, {"$set": user})
        mongo.db.items.find_one_and_update({"_id": ObjectId(item_id)}, {"$set": item})
    else:
        #Validate bid
        last_item = item["bid_history"][-1]
        if int(last_item["bidTime"]) < int(new_bid["bidTime"]) and float(last_item["bidPrice"]) < float(new_bid["bidPrice"]):
            # Only append bid if timestamp is newer and new bid must be greater
            item["bid_history"].append(new_bid)
            #Store in user's bidHistory
            user["bidHistory"].append(new_bid)
            mongo.db.users.find_one_and_update({"_id": new_bid["userID"]}, {"$set": user})
            mongo.db.items.find_one_and_update({"_id": ObjectId(item_id)}, {"$set": item})
            # Alert person who has been outbid
            alert = {"userID": last_item["userID"], "message": "You have been outbid for " + item["name"] + ".", "timestamp": time.time()*1000, "read": False}
            print("ALERT PREVIOUS BIDDER", alert)
            emit('alert', json.dumps(alert), broadcast=True)
    # Alert seller
    alert = {"userID": item["seller"], "message": "Your item " + item["name"] + " has received a bid.", "timestamp": time.time()*1000, "read": False}
    print("ALERT SELLER", alert)
    emit('alert', json.dumps(alert), broadcast=True)


    #broadcast data to all clients
    emit('bid', bid, broadcast=True)

@socketio.on('newNotification')
def handle_notification(notification):
    #receive new notification
    print("RECEIVED", notification)
    new_notification = json.loads(notification)
    # Store notification in user's db
    user_id = new_notification.pop("userID")
    user = mongo.db.users.find_one({"_id": user_id})
    user["notifications"].append(new_notification)
    mongo.db.users.find_one_and_update({"_id": user_id}, {"$set": user})
<<<<<<< HEAD
>>>>>>> master
=======
>>>>>>> 9b4d7c6582610cf32340691b91d8b936d0c78943

@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')



if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=os.environ.get('PORT', 3000), debug=True)
