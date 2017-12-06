from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

from database.config import engine

meta = MetaData(bind=engine)

Base = declarative_base(engine)

"""
    ORM SCHEMA LOAD FROM DATABASE
"""
class Histories(Base):
    __tablename__ = 'ChatHistories'
    __table_args__ = { 'autoload': True }

class Robots(Base):
    __tablename__ = 'Robots'
    __table_args__ = { 'autoload': True }

class Groups(Base):
    __tablename__ = 'QuestionGroups'
    __table_args__ = { 'autoload': True }

class Questions(Base):
    __tablename__ = 'Questions'
    __table_args__ = { 'autoload': True }

class Answers(Base):
    __tablename__ = 'Answers'
    __table_args__ = { 'autoload': True }

