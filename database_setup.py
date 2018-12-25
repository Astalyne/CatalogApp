from sqlalchemy import String, Integer, ForeignKey, Column, ForeignKeyConstraint,TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base= declarative_base()


class Category(Base):
    __tablename__= 'category'
    id=Column(Integer, primary_key=True)
    name= Column(String(50),nullable=False)

    @property
    def serialize(self):
        return {'name':self.name,'id':self.id,}

class User(Base):
    __tablename__='user'
    id=Column(Integer,primary_key=True)
    name=Column(String(50),nullable=False)
    @property
    def serialize(self):
        return{'id':self.id,'name':self.name,}

class Item(Base):

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    
    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,'created_at': self.created_at,
            'category': self.category_id}

engine=create_engine('sqlite:///catalogapp.db')
Base.metadata.create_all(engine)