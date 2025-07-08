# app.py (updated)
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
import locale
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Configure locales
try:
    locale.setlocale(locale.LC_ALL, 'French_France')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("⚠ Impossible de configurer une locale. Formats de dates par défaut utilisés.")

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "rayen1234")
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER', 'u59284_eB9v2rDNQP')}:"
    f"{os.getenv('DB_PASSWORD', 'mJMpY9v+ZTz.CltLlv4v!E+t')}@"
    f"{os.getenv('DB_HOST', '67.220.85.157')}:"
    f"{os.getenv('DB_PORT', '3306')}/"
    f"{os.getenv('DB_NAME', 's59284_casino_bot')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Constants
EURO_TO_DINAR = 4.5

# Models
class ClientPhoto(db.Model):
    __tablename__ = 'client_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    photo_data = db.Column(db.LargeBinary, nullable=False)
    photo_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    articles = db.Column(db.Text, nullable=False)
    prix_euro = db.Column(db.Numeric(10, 2), nullable=False)
    prix_dinar = db.Column(db.Numeric(10, 2), nullable=False)
    prix_vente = db.Column(db.Numeric(10, 2), nullable=False)
    gain = db.Column(db.Numeric(10, 2))
    reste_a_payer = db.Column(db.Numeric(10, 2))
    avance = db.Column(db.Numeric(10, 2), nullable=False)
    date_passation = db.Column(db.Date, nullable=False)
    date_livraison = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    photos = db.relationship('ClientPhoto', backref='client', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(Client, self).__init__(**kwargs)
        self.prix_dinar = float(self.prix_euro) * EURO_TO_DINAR
        self.gain = float(self.prix_vente) - float(self.prix_dinar)
        self.reste_a_payer = float(self.prix_vente) - float(self.avance)

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    if request.method == 'POST':
        try:
            # Process form data
            client = Client(
                numero=get_next_numero(),
                nom=request.form['nom'].strip(),
                articles=process_articles(request.form['articles']),
                prix_euro=float(request.form['prix_euro']),
                prix_vente=float(request.form['prix_vente']),
                avance=float(request.form['avance']),
                date_passation=datetime.strptime(request.form['date_passation'], '%d/%m/%Y').date(),
                date_livraison=datetime.strptime(request.form['date_livraison'], '%d/%m/%Y').date()
            )
            
            # Validate dates
            if client.date_livraison < client.date_passation:
                flash("La date de livraison doit être après la date de passation.", 'error')
                return redirect(url_for('index'))
            
            db.session.add(client)
            db.session.commit()
            
            # Handle photo uploads
            if 'photos' in request.files:
                files = request.files.getlist('photos')
                for file in files[:5]:  # Limit to 5 photos
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        photo = ClientPhoto(
                            client_id=client.id,
                            photo_data=file.read(),
                            photo_filename=filename
                        )
                        db.session.add(photo)
                
                db.session.commit()
            
            flash("✅ Données enregistrées avec succès.", 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            flash(f"⚠️ Erreur de saisie: {str(e)}", 'error')
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erreur technique: {str(e)}", 'error')
    
    return render_template('index.html', next_numero=get_next_numero())

@app.route('/security', methods=['GET', 'POST'])
def security_check():
    if request.method == 'POST':
        if request.form['secret_key'] == app.config['SECRET_KEY']:
            session['authenticated'] = True
            return redirect(url_for('index'))
        flash("Clé incorrecte!", 'error')
    return render_template('security.html')

@app.route('/clients')
def list_clients():
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    clients = Client.query.order_by(Client.numero.desc()).all()
    
    # Calculate totals
    totals = {
        'count': len(clients),
        'total_euro': sum(float(c.prix_euro) for c in clients),
        'total_dinar': sum(float(c.prix_dinar) for c in clients),
        'total_vente': sum(float(c.prix_vente) for c in clients),
        'total_gain': sum(float(c.gain) for c in clients),
        'total_avance': sum(float(c.avance) for c in clients),
        'total_reste': sum(float(c.reste_a_payer) for c in clients)
    }
    
    return render_template('clients.html', clients=clients, totals=totals)

@app.route('/client/<int:client_id>/photos')
def client_photos(client_id):
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    client = Client.query.get_or_404(client_id)
    return render_template('client_photos.html', client=client)

@app.route('/photo/<int:photo_id>')
def get_photo(photo_id):
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    photo = ClientPhoto.query.get_or_404(photo_id)
    return photo.photo_data, 200, {'Content-Type': 'image/jpeg', 'Content-Disposition': f'inline; filename={photo.photo_filename}'}

@app.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    client = Client.query.get_or_404(client_id)
    
    if request.method == 'POST':
        try:
            client.nom = request.form['nom'].strip()
            client.articles = process_articles(request.form['articles'])
            client.prix_euro = float(request.form['prix_euro'])
            client.prix_vente = float(request.form['prix_vente'])
            client.avance = float(request.form['avance'])
            client.date_passation = datetime.strptime(request.form['date_passation'], '%d/%m/%Y').date()
            client.date_livraison = datetime.strptime(request.form['date_livraison'], '%d/%m/%Y').date()
            
            # Recalculate derived fields
            client.prix_dinar = float(client.prix_euro) * EURO_TO_DINAR
            client.gain = float(client.prix_vente) - float(client.prix_dinar)
            client.reste_a_payer = float(client.prix_vente) - float(client.avance)
            
            # Validate dates
            if client.date_livraison < client.date_passation:
                flash("La date de livraison doit être après la date de passation.", 'error')
                return redirect(url_for('edit_client', client_id=client_id))
            
            # Handle photo uploads
            if 'photos' in request.files:
                files = request.files.getlist('photos')
                for file in files[:5]:  # Limit to 5 photos
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        photo = ClientPhoto(
                            client_id=client.id,
                            photo_data=file.read(),
                            photo_filename=filename
                        )
                        db.session.add(photo)
            
            db.session.commit()
            flash("✅ Client mis à jour avec succès.", 'success')
            return redirect(url_for('list_clients'))
            
        except ValueError as e:
            flash(f"⚠️ Erreur de saisie: {str(e)}", 'error')
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erreur technique: {str(e)}", 'error')
    
    return render_template('edit_client.html', client=client)

@app.route('/delete_photo/<int:photo_id>')
def delete_photo(photo_id):
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    photo = ClientPhoto.query.get_or_404(photo_id)
    client_id = photo.client_id
    db.session.delete(photo)
    db.session.commit()
    flash("✅ Photo supprimée avec succès.", 'success')
    return redirect(url_for('edit_client', client_id=client_id))

@app.route('/delete/<int:client_id>')
def delete_client(client_id):
    if 'authenticated' not in session:
        return redirect(url_for('security_check'))
    
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash(f"✅ Client N°{client.numero} ({client.nom}) supprimé avec succès.", 'success')
    return redirect(url_for('list_clients'))

# Helper functions
def get_next_numero():
    last_client = Client.query.order_by(Client.numero.desc()).first()
    return (last_client.numero + 1) if last_client else 1

def process_articles(articles_text):
    articles_list = [art.strip() for art in articles_text.split('\n') if art.strip()]
    count = len(articles_list)
    
    if ":" in articles_text:
        articles_text = articles_text.split(":", 1)[1].strip()
    
    return articles_text

# Run the app
if __name__ == '__main__':
    app.run(debug=True)