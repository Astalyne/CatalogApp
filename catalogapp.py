from flask import Flask, url_for,redirect,render_template,flash,request,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

app= Flask(__name__)

engine= create_engine('sqlite:///catalogapp.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession= sessionmaker(bind=engine)
session=DBSession()





#Returns JSON endpoint
@app.route('/JSON')
def CatalogJSON():
    return "Json"


#RootPage,Shows Catalog Categories and Recent Items
#If loggedin: can add item
@app.route('/')
@app.route('/Categories')
def showCategories():
    categories= session.query(Category).all()
    latest = session.query(Item).order_by(
    Item.created_at.desc()).limit(10).all()
    for c in latest:
        print (c.name)
        print ("   ")
        print (c.id)
    return render_template('categories.html',categories=categories,latest=latest)
    
#Specific choose category page, Shows all items
@app.route('/Categories/<int:category_id>')
def showCategory(category_id):
    category= session.query(Category).filter_by(id=category_id).one()
    items= session.query(Item).filter_by(category_id=category_id).all()
    
    return render_template('category.html',category=category,items=items)
    


#Shows Item page with description
#if loggedin: has edit and delete choice
@app.route('/Categories/<int:category_id>/<int:item_id>')
def showItem(category_id,item_id):
    item= session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html',item=item,category_id=category_id)


#Adds Item , takes in as input: Name description and category
@app.route('/Categories/add',
methods =['GET','POST'])
@app.route('/add',
methods =['GET','POST'])
def addItem(category_id):
    if request.method=='POST':
        newitem = Item(name=request.form['name'],
        description=request.form['description'],category_id=category_id) 
        session.add(newitem)
        session.commit()
        return redirect(url_for('showCategory',category_id=category_id))
    else:
        return render_template('addItem.html',category_id=category_id)
    # return render_template('addItem',category=category)

#Edits item ( name desc and category)
@app.route('/Categories/<int:category_id>/<int:item_id>/delete',
methods =['GET','POST'])
def deleteItem():
    return "this is to delete item"



#Deletes item 
@app.route('/Categories/<int:category_id>/<int:item_id>/delete',
methods =['GET','POST'])
def editItem():
    return "this is editing page"





if __name__=='__main__':
    app.debug=True
    app.run(host='0.0.0.0',port=5000)



