from sqlmodel import create_engine
import os

engine = create_engine(os.getenv('DATABASE_URL'))