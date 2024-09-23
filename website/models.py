from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)


class Admin(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('admin', uselist=False))

class Sponsor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('sponsor', uselist=False))

class Influencer(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    category = db.Column(db.String(120), nullable=False)
    niche = db.Column(db.String(120), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('influencer', uselist=False))

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    goals = db.Column(db.String(500), nullable=True) 
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))
    is_flagged = db.Column(db.Boolean, default=False)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    requirements = db.Column(db.String(500), nullable=True)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True, cascade="all, delete-orphan"))
    influencer = db.relationship('Influencer', backref=db.backref('ad_requests', lazy=True))
    is_flagged = db.Column(db.Boolean, default=False)


    def respond(self, status):
        if status in ['approved', 'rejected']:
            self.status = status
            db.session.commit()

class Statistic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    conversions = db.Column(db.Integer, nullable=False)
    campaign = db.relationship('Campaign', backref=db.backref('statistics', lazy=True))
