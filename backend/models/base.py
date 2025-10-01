# backend/models/base.py
from sqlalchemy.orm import declarative_base

# this class is inherited by all our tables defined in other files in this folder (models) 
Base = declarative_base()