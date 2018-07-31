from flask import (Flask, 
                   render_template, 
                   url_for, 
                   request, 
                   redirect, 
                   flash, 
                   jsonify, 
                   make_response)
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, relationship
from database_setup import Base, User, Category, Items
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os, random, string, datetime, json, httplib2, requests
# Import login_required from login_decorator.py
from login_decorator import login_required
from functools import wraps

# Create a Flask instance
app = Flask(__name__)

# Load GConnect CLIENT_ID and client_secrets JSON file in root folder
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Taipei Hair Salons"

# Connect to database
engine = create_engine('sqlite:///taipeihairsalons.db')
Base.metadata.bind = engine
# Create session
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Facebook Connect
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    #exchange client token for long-lived server-side token with GET
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.11/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print "data: ",data
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API
    # make API call with new token
    url = 'https://graph.facebook.com/v2.11/me?%s&fields=name,id,email,picture' % token

    #new: put the "picture" here, it is now part of the default "public_profile"

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['picture'] = data['picture']["data"]["url"]
    login_session['access_token'] = access_token

    #see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><img src="'
    output += login_session['picture']
    output += ' ">'

    flash("Now logged in as %s" % login_session['username'])
    return output
# End FB connect

# Begin FB disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# End FB disconnect

# GConnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

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
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

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
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    # saving the user state to the database for maintaining
    # and authentication.
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;' \
              'height: 300px;' \
              'border-radius: 150px;' \
              '-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;">' 
    flash("you are now logged in as %s" % login_session['username'])
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
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
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showCatalog'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
# End GDisconnect

# Begin General Disconnect function based on OAuth provider
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
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        # return gdisconnect function
        return redirect(url_for('gdisconnect'))
# End General Disconnect function

# Login - Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


#===================
# Flask Routing
#===================
# Homepage
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).order_by(desc(Items.date)).limit(5)
    return render_template('catalog.html',
                            categories = categories,
                            items = items)

# Category Items
@app.route('/catalog/<path:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).first()
    items = session.query(Items).filter_by(category=category).order_by(asc(Items.name)).all()
    print items
    count = session.query(Items).filter_by(category=category).count()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_items.html',
                                category = category.name,
                                categories = categories,
                                items = items,
                                count = count)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('items.html',
                                category = category.name,
                                categories = categories,
                                items = items,
                                count = count,
                                user=user)

# Display a Specific Item
@app.route('/catalog/<path:category_name>/<path:item_name>/')
def showItem(category_name, item_name):
    item = session.query(Items).filter_by(name=item_name).first()
    creator = getUserInfo(item.user_id)
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_itemdetail.html',
                                item = item,
                                category = category_name,
                                categories = categories,
                                creator = creator)
    else:
        return render_template('itemdetail.html',
                                item = item,
                                category = category_name,
                                categories = categories,
                                creator = creator)

# Add a category
@app.route('/catalog/addcategory', methods=['GET', 'POST'])
@login_required
def addCategory():
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        print newCategory
        session.add(newCategory)
        session.commit()
        flash('Category Successfully Added!')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('addcategory.html')

# Edit a category
@app.route('/catalog/<path:category_name>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    editedCategory = session.query(Category).filter_by(name=category_name).first()
    category = session.query(Category).filter_by(name=category_name).first()
    # TypeError: 'NoneType' object has no attribute '__getitem__'
    creator = getUserInfo(editedCategory['user_id'])
    user = getUserInfo(login_session.user_id)
    if creator.id != login_session['user_id']:
        flash ("You cannot edit this Category. This Category belongs to %s" % creator.name)
        return redirect(url_for('showCatalog'))
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash('Category Item Successfully Edited!')
        return  redirect(url_for('showCatalog'))
    else:
        return render_template('editcategory.html',
                                categories = editedCategory,
                                category = category)

# Delete a category
@app.route('/catalog/<path:category_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    categoryToDelete = session.query(Category).filter_by(name = category_name).first()
    # See if the logged in user is the owner of item
    # AttributeError: 'NoneType' object has no attribute 'user_id'
    creator = getUserInfo(categoryToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash ("You cannot delete this Category. This Category belongs to %s" % creator.name)
        return redirect(url_for('showCatalog'))
    if request.method =='POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('Category Successfully Deleted! '+ categoryToDelete.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletecategory.html',
                                category = categoryToDelete)

# Add an item
@app.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def addItem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Items(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['picture'],
            category=session.query(Category).filter_by(name=request.form['category']).one(),
            date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item Successfully Added!')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('additem.html',
                                categories=categories)

# Edit an item
@app.route('/<path:item_name>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_name):
    editedItem = session.query(Items).filter_by(name=item_name).first()
    categories = session.query(Category).all()
    user = getUserInfo(login_session['user_id'])
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        if request.form['category']:
            category = session.query(Category).filter_by(name=request.form['category']).one()
            editedItem.category = category
        time = datetime.datetime.now()
        editedItem.date = time
        session.add(editedItem)
        session.commit()
        flash('Category Item Successfully Edited!')
        return  redirect(url_for('showCategory', category_name=editedItem.category.name))
    else:
        return render_template('edititem.html', item=editedItem, categories=categories)

# Delete an item
@app.route('/<path:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_name):
    itemToDelete = session.query(Items).filter_by(name=item_name).first()    
    user = getUserInfo(login_session['user_id'])
    if request.method =='POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted! '+itemToDelete.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


# Begin JSON Routing 
# links working properly
@app.route('/catalog/JSON')
def allItemsJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        items = [i.serialize for i in session.query(Items)\
                    .filter_by(category_id=category_dict[c]["id"]).all()]
        if items:
            category_dict[c]["Item"] = items
    return jsonify(Category=category_dict)

@app.route('/catalog/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])

@app.route('/catalog/items/JSON')
def itemsJSON():
    items = session.query(Items).all()
    return jsonify(items=[i.serialize for i in items])

@app.route('/catalog/<path:category_name>/items/JSON')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category).all()
    return jsonify(items=[i.serialize for i in items])

@app.route('/catalog/<path:category_name>/<path:item_name>/JSON')
def ItemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(name=item_name,\
                                        category=category).one()
    return jsonify(item=[item.serialize])
# End JSON routing

# url_for static path processor
# remove when deployed
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# Always at end of file !Important!
if __name__ == '__main__':
    app.secret_key = 'DEV_SECRET_KEY'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)