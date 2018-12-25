import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name="Acoustic Guitars")
category2 = Category(name="Electric Guitars")
category3 = Category(name="Bass Guitars")
category4 = Category(name="Ukeleles")
category5 = Category(name="Drums")

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.commit()

item1 = Item(name="German Guitar",
             description="Classic Germany guitar.",category=category1,
             created_at=datetime.datetime.now()
            )
# item6 = Item(name="  Guitar",
#              description=" guitar.",category=category2,
#              created_at=datetime.datetime.now()
#             )

item2 = Item(name="Scottish Guitar",
             description="Scotland made this beauty and it tastes great.",category=category2,
             created_at=datetime.datetime.now())

item3 = Item(name="The One Guitar",
             description="A guitar that works.",category=category3,
             created_at=datetime.datetime.now())

item4 = Item(name="Unknown Brand",
             description="Found in a ditch",category=category4,
             created_at=datetime.datetime.now())

item5 = Item(name="Boom Drumsticks",
             description="BarumCHat",category=category5,
             created_at=datetime.datetime.now())
session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)
session.add(item5)
# session.add(item6)
session.commit()