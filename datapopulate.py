import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name="Acoustic Guitars")
category2 = Category(name="Electric Guitars")
category3 = Category(name="Bass Guitars")
category4 = Category(name="Ukeleles")
category5 = Category(name="Mandolins")
category6 = Category(name="Banjos")
category7 = Category(name="Guitar Amplifiers")
category8 = Category(name="Effects Pedals")
category9 = Category(name="Drums")

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.add(category6)
session.add(category7)
session.add(category8)
session.add(category9)
session.commit()

item1 = Item(name="Awesome Acoustic Guitar",
             description="An awesome acoustic guitar."
            )

item2 = Item(name="Sublime Electric Guitar",
             description="A sublime electric guitar.")

item3 = Item(name="Wunderkind Bass Guitar",
             description="A bass guitar for wunderkinds.")

item4 = Item(name="Unholy Ukelele",
             description="An unholy ukelele.")

item5 = Item(name="Merry Mandolin",
             description="The merriest of mandolins.")

item6 = Item(name="Blistering Banjo",
             description="A blistering banjo.")

item7 = Item(name="High Altitude Amplifier",
             description="A guitar amp for the heights.")

item8 = Item(name="Effects Pedals in Triplicate",
             description="More effects pedals than you could ever want.")

item9 = Item(name="The Pounding Drums",
             description="A drum for every occasion.")

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)
session.add(item5)
session.add(item6)
session.add(item7)
session.add(item8)
session.add(item9)
session.commit()