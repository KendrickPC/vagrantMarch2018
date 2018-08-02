from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_setup import *

# https://stackoverflow.com/questions/4526498/sqlalchemy-declarative-syntax-with-autoload-reflection-in-pylons
# Binds metadata to the engine in the init_model function.
# If the meta.Base.metadata.bind(engine) statement successfully
# binds your model metadata to the engine, you should be able to 
# perform this initialization in your own init_model function.
engine = create_engine('sqlite:///taipeihairsalons.db')

 # Written to avoid specifying autoload-with for each table
 # added this line at the end of init_model():
Base.metadata.bind = engine

# https://stackoverflow.com/questions/29826169/using-sqlalchemy-sessions-and-transactions
# Creates the session once, globally, to initialize and transact the database. 
DBSession = sessionmaker(bind=engine)
session = DBSession()

# If Category exists, this deletes session information from database. 
session.query(Category).delete()
# If Items exists, this deletes sesssion information from database. 
session.query(Items).delete()
# If User exists,  this deletes session information from databse. 
session.query(User).delete()

# Create Bart Simpson as first user
User1 = User(name="Bart Simpson",
             email="bartsimpson@gmail.com",
             picture='https://upload.wikimedia.org/wikipedia/en/7/70/Bart_Simpson_-_Skateboarding.png')
session.add(User1)
session.commit()

# Create Taipei District #1 under Category variable
Category1 = Category(name="Songshan District",
                     user_id=1)
session.add(Category1)
session.commit()

Category2 = Category(name="Zhongshan District",
                     user_id=1)
session.add(Category2)
session.commit

Category3 = Category(name="Xinyi District",
                     user_id=1)
session.add(Category3)
session.commit()

Category4 = Category(name="Da'an District",
                     user_id=1)
session.add(Category4)
session.commit()

Category5 = Category(name="Zhongzheng District",
                     user_id=1)
session.add(Category5)
session.commit()

# Populate a category with items for testing
# Using different users for items also
Item1 = Items(name="Bart Simpson Skateboarding",
              date=datetime.datetime.now(),
              description="Bart Simpsons Skateboarding.",
              picture="http://www.freepngimg.com/download/bart_simpson/1-2-bart-simpson-png-image.png",
              category_id=1,
              user_id=1)
session.add(Item1)
session.commit()

Item2 = Items(name="Bart Simpson Chilling",
              date=datetime.datetime.now(),
              description="Chill Bart.",
              picture="https://vignette.wikia.nocookie.net/simpsons/images/7/7c/Bart_Simpson_Season_25_Official.jpg/revision/latest?cb=20140511110240",
              category_id=1,
              user_id=1)
session.add(Item2)
session.commit()

Item3 = Items(name="Bart Simpson Mooning",
              date=datetime.datetime.now(),
              description="Bart Mooning.",
              picture="https://img.elo7.com.br/product/zoom/19C2B6E/adesivo-bart-simpsons-simpsons.jpg",
              category_id=1,
              user_id=1)
session.add(Item3)
session.commit()

print "Your database has been populated with Songshan District data!"
