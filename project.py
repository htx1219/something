from flask import Flask, render_template, request, redirect, jsonify, \
                  url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Item Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///item_catalog_with_users.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    stored_provider = login_session.get('provider')
    if stored_access_token is not None and gplus_id == stored_gplus_id \
       and stored_provider == 'google':
        response = make_response(json.dumps('Current user is already connected.'),  # noqa
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Add provide to login session
    login_session['provider'] = 'google'

    # See if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style="width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def create_user(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect from google - Revoke a current user's token
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    return result['status'] == '200'


# JSON APIs to view Category Information
@app.route('/catalog/<int:category_id>/item/JSON')
def category_item_json(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/item/<int:item_id>/JSON')
def item_json(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/catalog/JSON')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/catalog/')
def show_categories():
    categories = session.query(Category).order_by(asc(Category.name))
    recent_items = session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template('index.html', categories=categories,
                           recent_items=recent_items)


# Show all items under a category
@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/item/')
def show_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id) \
                   .order_by(desc(Item.id)).all()
    return render_template('category.html', items=items, category=category)


# Show an item under a category
@app.route('/catalog/<int:category_id>/item/<int:item_id>/')
def show_item(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    creator = get_user_info(item.user_id)
    return render_template('item.html', item=item, creator=creator,
                           category=category)


# Create a new item
@app.route('/catalog/<int:category_id>/item/new/', methods=['GET', 'POST'])
def new_item(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        new_item = Item(name=request.form['name'],
                        description=request.form['description'],
                        category_id=category_id,
                        user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('New %s Item Successfully Created' % (new_item.name))
        return redirect(url_for('show_category', category_id=category_id))
    else:
        return render_template('new_item.html', category_id=category_id)


# Edit an item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    edited_item = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != edited_item.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. You can only edit item created by yourself.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        if request.form['category']:
            category = session.query(Category) \
                              .filter_by(name=request.form['category']).first()
            if category is None:
                flash('Fail to edit due to invalid category!')
                return redirect(url_for('show_item', category_id=category_id,
                                        item_id=item_id))
            edited_item.category = category
        session.add(edited_item)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('show_item',
                                category_id=edited_item.category.id,
                                item_id=item_id))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('edit_item.html', categories=categories,
                               item=edited_item)


# Delete an item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    item_to_delete = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item_to_delete.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. You can only delete item created by yourself.');}</script><body onload='myFunction()''>"  # noqa
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('show_category', category_id=category_id))
    else:
        return render_template('delete_item.html', item=item_to_delete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_categories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_categories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

