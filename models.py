from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Landlord(db.Model):
    __tablename__ = "landlord"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(250))
    location = db.Column(db.String(250))
    property_count = db.Column(db.Integer)
    group_id = db.Column(db.String(50))


    def __repr__(self):
        return '<Landlord %r>' % self.name

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Property(db.Model):
    __tablename__ = "property"
    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    house_number = db.Column(db.Integer)
    street_name = db.Column(db.String(250))
    zip_code = db.Column(db.String(10))
    property_type = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey("landlord.id"))
    owner = db.relationship("Landlord", backref="properties")
    service_call_count = db.Column(db.Integer)
    tenant_complaints = db.Column(db.Integer)
    health_violation_count = db.Column(db.Integer)
    court_case_count = db.Column(db.Integer)
    owner_occupied = db.Column(db.String(250))
    inspection_count = db.Column(db.Integer)
    code_violations_count = db.Column(db.Integer)
    is_business = db.Column(db.String(250))
    public_owner = db.Column(db.String(250))
    business_entity_type = db.Column(db.String(250))
    current_use = db.Column(db.String(250))
    police_incidents_count = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    # TODO: GroupID is duplicated here: should only exist with Landlord
    group_id = db.Column(db.String(50))
    

    def __repr__(self):
        return '<Property %r>' % self.address

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

