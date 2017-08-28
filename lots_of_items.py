from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('postgresql://catalog:catalog@localhost:5432/fsnd_catalog')
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


# Create admin user
user1 = User(name="Tianxiao Huang", email="htx1219@gmail.com",
             picture="https://media.licdn.com/mpr/mpr/shrinknp_400_400/p/8/005/05c/3cd/32fdbc1.jpg")  # noqa
session.add(user1)
session.commit()

# Create another user
user2 = User(name="Someone Else", email="idontexist@gmail.com",
             picture="static/blank_user.gif")  # noqa
session.add(user2)
session.commit()


# Category Music
category1 = Category(name="Music")

session.add(category1)
session.commit()


item1 = Item(user_id=1, name="Pop", category=category1,
             description="a genre of popular music that originated in its modern form in the United States and United Kingdom during the mid-1950s.")  # noqa

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Folk", category=category1,
             description="includes both traditional music and the genre that evolved from it during the 20th century folk revival.")  # noqa

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Classical", category=category1,
             description="art music produced or rooted in the traditions of Western music, including both liturgical (religious) and secular music.")  # noqa

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Rock", category=category1,
             description="a genre of popular music that originated as \"rock and roll\" in the United States in the early 1950s")  # noqa

session.add(item4)
session.commit()

item5 = Item(user_id=2, name="Jazz", category=category1,
             description="a music genre that originated in African American communities of New Orleans, United States, in the late 19th and early 20th centuries, and developed from roots in blues and ragtime.")  # noqa

session.add(item5)
session.commit()


# Category Sports
category2 = Category(name="Sport")

session.add(category2)
session.commit()


item1 = Item(user_id=2, name="Football", category=category2, description="American Football, or rugby")  # noqa

session.add(item1)
session.commit()

item2 = Item(user_id=2, name="Soccer", category=category2,
                     description="More commonly known as football or association football, is a team sport played between two teams of eleven players with a spherical ball.")  # noqa

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Tennis", category=category2,
             description="A racket sport that can be played individually against a single opponent (singles) or between two teams of two players each (doubles)")  # noqa

session.add(item3)
session.commit()


# Category Food
category3 = Category(name="Food")

session.add(category3)
session.commit()


item1 = Item(user_id=1, name="Pho", category=category3,
             description="a Vietnamese noodle soup consisting of broth, linguine-shaped rice noodles called banh pho, a few herbs, and meat.")  # noqa

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Chinese Dumplings", category=category3,
             description="a common Chinese dumpling which generally consists of minced meat and finely chopped vegetables wrapped into a piece of dough skin. The skin can be either thin and elastic or thicker.")  # noqa

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Gyoza", category=category3,
             description="light seasoning of Japanese gyoza with salt and soy sauce, and in a thin gyoza wrapper")  # noqa

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Stinky Tofu", category=category3,
             description="Taiwanese dish, deep fried fermented tofu served with pickled cabbage.")  # noqa

session.add(item4)
session.commit()


# Category Others
category4 = Category(name="Other")

session.add(category4)
session.commit()

print "added catalog items!"
