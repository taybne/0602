from flask import Flask, render_template, request, jsonify
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib import sqla
from datetime import datetime
import json
import os

# ИЗМЕНИЛ template_folder НА ТВОЮ ПАПКУ
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-change-it'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tag.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===== ТВОИ МОДЕЛИ (оставил как есть) =====
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref='locations')
    theme = db.Column(db.String(50))
    photos = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    city = db.Column(db.String(100))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    user_id = db.Column(db.String(50))
    nickname = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===== АДМИНКА =====
admin = Admin(app, name='THEARCGO Admin')
admin.add_view(sqla.ModelView(City, db.session))
admin.add_view(sqla.ModelView(Location, db.session))
admin.add_view(sqla.ModelView(Suggestion, db.session))

# ===== ТВОИ API (оставил как есть) =====
@app.route('/api/suggest', methods=['POST'])
def suggest():
    data = request.json
    suggestion = Suggestion(
        type=data['type'],
        city=data['city'],
        title=data.get('title'),
        description=data.get('description'),
        user_id=data['user_id'],
        nickname=data['nickname']
    )
    db.session.add(suggestion)
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/api/cities')
def get_cities():
    cities = City.query.all()
    return jsonify([{'name': c.name, 'slug': c.slug} for c in cities])

@app.route('/api/locations/<city_slug>')
def get_locations(city_slug):
    city = City.query.filter_by(slug=city_slug).first()
    if not city:
        return jsonify([])
    locations = Location.query.filter_by(city_id=city.id, approved=True).all()
    return jsonify([{
        'title': l.title,
        'desc': l.description or '',
        'theme': l.theme or 'popular',
        'photos': json.loads(l.photos or '[]')
    } for l in locations])

@app.route("/")
def index():
  return render_template("index.html")
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)



