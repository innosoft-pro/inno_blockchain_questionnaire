from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbms.db_config import db_connection

BASE = declarative_base()


class SessionModel(BASE):
    __tablename__ = 'session'

    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    expired = Column(Integer, default=0)
    last_access_time = Column(DateTime)
    current_step = Column(Integer)
    current_process = Column(Integer)
    process_params = Column(String(10000))
    current_param = Column(Integer)


class ProcessModel(BASE):
    __tablename__ = 'process'

    process_id = Column(Integer, primary_key=True)
    process_flow = Column(JSON)

class UsersSurveysModel(BASE):
    __tablename__ = 'user_survey'

    user_id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, primary_key=True)


engine = create_engine(db_connection)
BASE.metadata.create_all(engine)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()
