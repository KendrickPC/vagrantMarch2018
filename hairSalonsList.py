from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils import database_exists, drop_database, create_database

from database_setup import Category, CategoryItem, User, Base

engine = create_engine('sqlite:///hairSalonsCatalog.db')

# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
user1 = User(name="Bart Simpson", email="BartSimpson@gmail.com",
             picture='http://freevectorlogo.net/bart-simpson/34856')
session.add(user1)
session.commit()

# Items for Strings
category1 = Category(name="Xinyi District", user_id=1)

session.add(category1)
session.commit()

item1 = CategoryItem(name="Xinyi Hair Salon #1", user_id=1, description="Xinyi District Z", category=category1)

session.add(item1)
session.commit()

item2 = CategoryItem(name="Xinyi Hair Salon #2", user_id=1,  description="Xinyi District Y", category=category1)

session.add(item2)
session.commit()

item3 = CategoryItem(name="Xinyi Hair Salon #3", user_id=1, description="Xinyi District X", category=category1)

session.add(item3)
session.commit()

# Items for Woodwinds
category2 = Category(name="Zhongshan District", user_id=1)

session.add(category2)
session.commit()

item1 = CategoryItem(name="Zhongshan Hair Salon #1", user_id=1, description="Zhongshan District Z", category=category2)

session.add(item1)
session.commit()

item2 = CategoryItem(name="Zhongshan Hair Salon #2", user_id=1,  description="Zhongshan District Y", category=category2)

session.add(item2)
session.commit()

item3 = CategoryItem(name="Zhongshan Hair Salon #3", user_id=1, description="Zhongshan District X", category=category2)

session.add(item3)
session.commit()

# Items for Percussion
category3 = Category(name="Songshan District", user_id=1)

session.add(category3)
session.commit()

item1 = CategoryItem(name="Songshan Hair Salon #1", user_id=1, description="Songshan District Z", category=category3)

session.add(item1)
session.commit()

item2 = CategoryItem(name="Songshan Hair Salon #2", user_id=1, description="Songshan District Y", category=category3)

session.add(item2)
session.commit()

item3 = CategoryItem(name="Songshan Hair Salon #3", user_id=1, description="Songshan District X", category=category3)

session.add(item3)
session.commit()

# Items for Brass
category4 = Category(name="Da'an", user_id=1)

session.add(category4)
session.commit()


categories = session.query(Category).all()
for category in categories:
    print "Category: " + category.name