from flask import Flask, url_for, redirect, render_template, flash, request, jsonify
from sqlalchemy import create_engine
import datetime
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
import random
import string
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open(
    'client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data

    try:
   
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


engine = create_engine('sqlite:///catalogapp.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#Returns JSON endpoint
@app.route('/JSON')
def CatalogJSON():
    all = []
    categories = session.query(Category).all()
    for i in categories:
        item = session.query(Item).filter_by(category_id=i.id).all()
        all.append(i.serialize)
        all[-1]['items'] = [s.serialize for s in item]
    return jsonify(categories=all)


# RootPage,Shows Catalog Categories and Recent Items
# If loggedin: can add item
@app.route('/')
@app.route('/Categories')
def showCategories():
    categories = session.query(Category).all()
    latest = session.query(Item).order_by(
    Item.created_at.desc()).limit(10).all()
    for c in latest:
        print (c.name)
        print ("   ")
        print (c.id)
    return render_template('categories.html', categories=categories, latest=latest)

# Specific choose category page, Shows all items
@app.route('/Categories/<int:category_id>')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()

    return render_template('category.html', category=category, items=items)


#Shows Item page with description
#if loggedin: has edit and delete choice
@app.route('/Categories/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item=item, category_id=category_id)


#Adds Item , takes in as input: Name description and category
@app.route('/Categories/add',
methods=['GET', 'POST'])
@app.route('/add',
methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect(url_for('showCategories'))
    categories = session.query(Category).all()
    if request.method =='POST':
        if item.creator(s_user_id/creator_email != login_session['user_id']/user_session['user']['email']):
            return "<script>function myFunction() {alert('You\
                are not authorized to delete this item.\
                Please create your own item in order\
                to delete.');}</script><body onload='myFunction()'>"
        newitem = Item(name=request.form['name'],
        description = request.form['description'],
        category_id=int(request.form['category']),
        created_at=datetime.datetime.now())
        session.add(newitem)
        session.commit()
        return redirect(url_for(
            'showItem', category_id=newitem.category_id, item_id=newitem.id))
    else:
        return render_template('addItem.html', categories=categories)
    # return render_template('addItem',category=category)

#Edits item ( name desc and category)
@app.route(
    '/Categories/<int:category_id>/<int:item_id>/delete',methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('showCategories'))
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if item.creator(s_user_id/creator_email != login_session['user_id']/user_session['user']['email']):
            return "<script>function myFunction() {alert('You\
                are not authorized to delete this item.\
                Please create your own item in order\
                to delete.');}</script><body onload='myFunction()'>"
        session.delete(item)
        session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    return render_template('deleteItem.html', item=item)


#Deletes item
@app.route(
    '/Categories/<int:category_id>/<int:item_id>/edit',methods=['GET', 'POST'])
def editItem(category_id, item_id):
    
    if 'username' not in login_session:
        return redirect(url_for('showCategories'))
    item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':
        if item.creator(s_user_id/creator_email != login_session['user_id']/user_session['user']['email']):
            return "<script>function myFunction() {alert('You\
                are not authorized to delete this item.\
                Please create your own item in order\
                to delete.');}</script><body onload='myFunction()'>"

        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        return redirect(url_for(
            'showCategory', category_id=category_id))
    else:
        return render_template(
            'editItem.html', category_id=category_id, item_id=item_id, item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
