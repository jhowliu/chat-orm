from __future__ import unicode_literals

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import *

# [driver]://user:password@host/dbname
engine = create_engine('mysql://{}:{}@192.168.10.14/{}?charset=utf8' \
            .format(USERNAME, PASSWORD, DATABASE))


Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

sess = Session()
