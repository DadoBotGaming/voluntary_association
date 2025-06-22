from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql # PyMySQL importato ma non direttamente usato nel codice Flask se usi SQLAlchemy con URI mysql+pymysql

pymysql.install_as_MySQLdb() # Necessario se usi SQLAlchemy con MySQL e PyMySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'la_tua_chiave_segreta_super_difficile' # Cambia questa chiave!
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/volontariato_db' # Aggiorna con le tue credenziali
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelli SQLAlchemy ---
class Utenti(db.Model):
    ID_Utente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(255), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    Nome = db.Column(db.String(100))
    Cognome = db.Column(db.String(100))
    Ruolo = db.Column(db.Enum('Admin', 'Volontario'), default='Volontario')
    DataCreazione = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def set_password(self, password):
        self.Password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Password, password)

class Famiglie(db.Model):
    ID_Famiglia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NomeFamiglia = db.Column(db.String(255), nullable=False)
    ReferenteNome = db.Column(db.String(100))
    ReferenteCognome = db.Column(db.String(100))
    NumeroMembri = db.Column(db.Integer)
    NumeroUomini = db.Column(db.Integer, default=0)
    NumeroDonne = db.Column(db.Integer, default=0)
    NumeroBambini = db.Column(db.Integer, default=0)
    Indirizzo = db.Column(db.String(255))
    NumeroTelefono = db.Column(db.String(20))
    Email = db.Column(db.String(255))
    SettimanaDistribuzione = db.Column(db.Integer)
    TipoDistribuzione = db.Column(db.Enum('Casa', 'Centro'))
    Note = db.Column(db.Text)
    DataRegistrazione = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Prodotti(db.Model):
    ID_Prodotto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NomeProdotto = db.Column(db.String(255), nullable=False)
    Descrizione = db.Column(db.Text)
    UnitaMisura = db.Column(db.String(50))
    inventario = db.relationship('Inventario', backref='prodotto', lazy=True)

class Inventario(db.Model):
    ID_VoceInventario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Prodotto = db.Column(db.Integer, db.ForeignKey('prodotti.ID_Prodotto'), nullable=False)
    Quantita = db.Column(db.Numeric(10, 2), nullable=False)
    DataScadenza = db.Column(db.Date)
    DataInserimento = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    DataUltimaModifica = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class CarichiInventario(db.Model):
    ID_Carico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Prodotto = db.Column(db.Integer, db.ForeignKey('prodotti.ID_Prodotto'))
    QuantitaCaricata = db.Column(db.Numeric(10, 2), nullable=False)
    DataCarico = db.Column(db.Date, nullable=False)
    Fornitore = db.Column(db.String(255))
    Note = db.Column(db.Text)
    DataRegistrazione = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    ID_UtenteRegistrazione = db.Column(db.Integer, db.ForeignKey('utenti.ID_Utente'))

class Progetti(db.Model):
    ID_Progetto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NomeProgetto = db.Column(db.String(255), nullable=False)
    Descrizione = db.Column(db.Text)
    DataInizio = db.Column(db.Date)
    DataFine = db.Column(db.Date)
    Stato = db.Column(db.Enum('In Corso', 'Completato', 'Pianificato'), default='Pianificato')
    ImmagineURL = db.Column(db.String(255))

class Attivita(db.Model):
    ID_Attivita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Progetto = db.Column(db.Integer, db.ForeignKey('progetti.ID_Progetto'), nullable=True)
    NomeAttivita = db.Column(db.String(255), nullable=False)
    Descrizione = db.Column(db.Text)
    DataAttivita = db.Column(db.DateTime)
    Luogo = db.Column(db.String(255))
    ImmagineURL = db.Column(db.String(255))

class Notizie(db.Model):
    ID_Notizia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titolo = db.Column(db.String(255), nullable=False)
    Contenuto = db.Column(db.Text, nullable=False)
    DataPubblicazione = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    Autore = db.Column(db.String(100))
    ImmagineURL = db.Column(db.String(255))
    Categoria = db.Column(db.String(100))

class Distribuzioni(db.Model):
    ID_Distribuzione = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Famiglia = db.Column(db.Integer, db.ForeignKey('famiglie.ID_Famiglia'))
    DataDistribuzione = db.Column(db.Date, nullable=False)
    Note = db.Column(db.Text)
    ID_VolontarioConsegna = db.Column(db.Integer, db.ForeignKey('utenti.ID_Utente'))
    Stato = db.Column(db.Enum('Pianificata', 'Completata', 'Annullata'), default='Pianificata')
    DataCreazione = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    dettagli = db.relationship('DettaglioDistribuzione', backref='distribuzione', lazy=True)


class DettaglioDistribuzione(db.Model):
    ID_DettaglioDistribuzione = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Distribuzione = db.Column(db.Integer, db.ForeignKey('distribuzioni.ID_Distribuzione'), nullable=False)
    ID_Prodotto = db.Column(db.Integer, db.ForeignKey('prodotti.ID_Prodotto'), nullable=False)
    QuantitaDistribuita = db.Column(db.Numeric(10, 2), nullable=False)

class Appuntamenti(db.Model):
    ID_Appuntamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Famiglia = db.Column(db.Integer, db.ForeignKey('famiglie.ID_Famiglia'), nullable=True)
    ID_Attivita = db.Column(db.Integer, db.ForeignKey('attivita.ID_Attivita'), nullable=True)
    Titolo = db.Column(db.String(255))
    DataOraAppuntamento = db.Column(db.DateTime, nullable=False)
    Luogo = db.Column(db.String(255))
    Note = db.Column(db.Text)
    Stato = db.Column(db.Enum('Pianificato', 'Confermato', 'Annullato', 'Completato'), default='Pianificato')
    DataCreazione = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())


# --- Route di Autenticazione ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nome = data.get('nome')
    cognome = data.get('cognome')
    ruolo = data.get('ruolo', 'Volontario') # Default a Volontario

    if not email or not password:
        return jsonify({'message': 'Email e password sono obbligatori'}), 400

    if Utenti.query.filter_by(Email=email).first():
        return jsonify({'message': 'Utente già registrato'}), 409

    nuovo_utente = Utenti(Email=email, Nome=nome, Cognome=cognome, Ruolo=ruolo)
    nuovo_utente.set_password(password)
    db.session.add(nuovo_utente)
    try:
        db.session.commit()
        return jsonify({'message': 'Utente registrato con successo'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Errore durante la registrazione'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email e password sono obbligatori'}), 400

    utente = Utenti.query.filter_by(Email=email).first()

    if utente and utente.check_password(password):
        session['user_id'] = utente.ID_Utente
        session['user_role'] = utente.Ruolo
        return jsonify({'message': 'Login effettuato con successo', 'user_id': utente.ID_Utente, 'ruolo': utente.Ruolo}), 200
    else:
        return jsonify({'message': 'Credenziali non valide'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear() # Rimuove tutte le chiavi dalla sessione
    return jsonify({'message': 'Logout effettuato con successo'}), 200

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'user_id': session['user_id'], 'user_role': session.get('user_role')}), 200
    else:
        return jsonify({'logged_in': False}), 200

# --- Helpers per la protezione delle route ---
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Autenticazione richiesta'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Autenticazione richiesta'}), 401
        if session.get('user_role') != 'Admin':
            return jsonify({'message': 'Accesso non autorizzato: richiesto ruolo Admin'}), 403
        return f(*args, **kwargs)
    return decorated_function


# --- Route API per Famiglie ---
@app.route('/api/famiglie', methods=['POST'])
@login_required # o @admin_required se solo admin possono aggiungere
def aggiungi_famiglia():
    data = request.get_json()
    try:
        nuova_famiglia = Famiglie(
            NomeFamiglia=data['NomeFamiglia'],
            ReferenteNome=data.get('ReferenteNome'),
            ReferenteCognome=data.get('ReferenteCognome'),
            NumeroMembri=data.get('NumeroMembri'),
            NumeroUomini=data.get('NumeroUomini', 0),
            NumeroDonne=data.get('NumeroDonne', 0),
            NumeroBambini=data.get('NumeroBambini', 0),
            Indirizzo=data.get('Indirizzo'),
            NumeroTelefono=data.get('NumeroTelefono'),
            Email=data.get('Email'),
            SettimanaDistribuzione=data.get('SettimanaDistribuzione'),
            TipoDistribuzione=data.get('TipoDistribuzione'),
            Note=data.get('Note')
        )
        db.session.add(nuova_famiglia)
        db.session.commit()
        return jsonify({'message': 'Famiglia aggiunta con successo', 'id': nuova_famiglia.ID_Famiglia}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/famiglie', methods=['GET'])
@login_required
def get_famiglie():
    try:
        lista_famiglie = Famiglie.query.all()
        famiglie_json = [{
            'ID_Famiglia': f.ID_Famiglia, 'NomeFamiglia': f.NomeFamiglia, 'ReferenteNome': f.ReferenteNome,
            'ReferenteCognome': f.ReferenteCognome, 'NumeroMembri': f.NumeroMembri, 'NumeroUomini': f.NumeroUomini,
            'NumeroDonne': f.NumeroDonne, 'NumeroBambini': f.NumeroBambini, 'Indirizzo': f.Indirizzo,
            'NumeroTelefono': f.NumeroTelefono, 'Email': f.Email,
            'SettimanaDistribuzione': f.SettimanaDistribuzione, 'TipoDistribuzione': f.TipoDistribuzione,
            'Note': f.Note, 'DataRegistrazione': f.DataRegistrazione.isoformat() if f.DataRegistrazione else None
        } for f in lista_famiglie]
        return jsonify(famiglie_json), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/famiglie/<int:id_famiglia>', methods=['GET'])
@login_required
def get_famiglia(id_famiglia):
    try:
        famiglia = Famiglie.query.get_or_404(id_famiglia)
        return jsonify({
            'ID_Famiglia': famiglia.ID_Famiglia, 'NomeFamiglia': famiglia.NomeFamiglia, 'ReferenteNome': famiglia.ReferenteNome,
            'ReferenteCognome': famiglia.ReferenteCognome, 'NumeroMembri': famiglia.NumeroMembri, 'NumeroUomini': famiglia.NumeroUomini,
            'NumeroDonne': famiglia.NumeroDonne, 'NumeroBambini': famiglia.NumeroBambini, 'Indirizzo': famiglia.Indirizzo,
            'NumeroTelefono': famiglia.NumeroTelefono, 'Email': famiglia.Email,
            'SettimanaDistribuzione': famiglia.SettimanaDistribuzione, 'TipoDistribuzione': famiglia.TipoDistribuzione,
            'Note': famiglia.Note, 'DataRegistrazione': famiglia.DataRegistrazione.isoformat() if famiglia.DataRegistrazione else None
        }), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


@app.route('/api/famiglie/<int:id_famiglia>', methods=['PUT'])
@login_required # o @admin_required
def modifica_famiglia(id_famiglia):
    famiglia = Famiglie.query.get_or_404(id_famiglia)
    data = request.get_json()
    try:
        famiglia.NomeFamiglia = data.get('NomeFamiglia', famiglia.NomeFamiglia)
        famiglia.ReferenteNome = data.get('ReferenteNome', famiglia.ReferenteNome)
        famiglia.ReferenteCognome = data.get('ReferenteCognome', famiglia.ReferenteCognome)
        famiglia.NumeroMembri = data.get('NumeroMembri', famiglia.NumeroMembri)
        famiglia.NumeroUomini = data.get('NumeroUomini', famiglia.NumeroUomini)
        famiglia.NumeroDonne = data.get('NumeroDonne', famiglia.NumeroDonne)
        famiglia.NumeroBambini = data.get('NumeroBambini', famiglia.NumeroBambini)
        famiglia.Indirizzo = data.get('Indirizzo', famiglia.Indirizzo)
        famiglia.NumeroTelefono = data.get('NumeroTelefono', famiglia.NumeroTelefono)
        famiglia.Email = data.get('Email', famiglia.Email)
        famiglia.SettimanaDistribuzione = data.get('SettimanaDistribuzione', famiglia.SettimanaDistribuzione)
        famiglia.TipoDistribuzione = data.get('TipoDistribuzione', famiglia.TipoDistribuzione)
        famiglia.Note = data.get('Note', famiglia.Note)
        db.session.commit()
        return jsonify({'message': 'Famiglia modificata con successo'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/famiglie/<int:id_famiglia>', methods=['DELETE'])
@admin_required # Solo admin possono eliminare
def elimina_famiglia(id_famiglia):
    famiglia = Famiglie.query.get_or_404(id_famiglia)
    try:
        # Considerare cosa fare con le distribuzioni/appuntamenti collegati
        # Si potrebbe impedire l'eliminazione se ci sono record collegati o eliminarli a cascata (configurando il DB)
        db.session.delete(famiglia)
        db.session.commit()
        return jsonify({'message': 'Famiglia eliminata con successo'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


# --- Route API per Prodotti e Inventario ---
@app.route('/api/prodotti', methods=['POST'])
@admin_required
def aggiungi_prodotto():
    data = request.get_json()
    try:
        nuovo_prodotto = Prodotti(
            NomeProdotto=data['NomeProdotto'],
            Descrizione=data.get('Descrizione'),
            UnitaMisura=data.get('UnitaMisura')
        )
        db.session.add(nuovo_prodotto)
        db.session.commit()
        return jsonify({'message': 'Prodotto aggiunto con successo', 'id': nuovo_prodotto.ID_Prodotto}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/prodotti', methods=['GET'])
@login_required
def get_prodotti():
    try:
        lista_prodotti = Prodotti.query.all()
        prodotti_json = [{
            'ID_Prodotto': p.ID_Prodotto, 'NomeProdotto': p.NomeProdotto,
            'Descrizione': p.Descrizione, 'UnitaMisura': p.UnitaMisura
        } for p in lista_prodotti]
        return jsonify(prodotti_json), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/inventario', methods=['POST'])
@admin_required # Aggiungere una voce all'inventario (non un carico)
def aggiungi_voce_inventario():
    data = request.get_json()
    try:
        nuova_voce = Inventario(
            ID_Prodotto=data['ID_Prodotto'],
            Quantita=data['Quantita'],
            DataScadenza=data.get('DataScadenza') # Assicurarsi che il formato sia YYYY-MM-DD
        )
        db.session.add(nuova_voce)
        db.session.commit()
        return jsonify({'message': 'Voce inventario aggiunta', 'id': nuova_voce.ID_VoceInventario}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


@app.route('/api/inventario', methods=['GET'])
@login_required
def get_inventario():
    try:
        voci_inventario = db.session.query(
                Inventario.ID_VoceInventario,
                Prodotti.NomeProdotto,
                Inventario.Quantita,
                Inventario.UnitaMisura, # Assumendo che UnitaMisura sia in Prodotti
                Inventario.DataScadenza,
                Inventario.DataInserimento
            ).join(Prodotti, Inventario.ID_Prodotto == Prodotti.ID_Prodotto)\
            .order_by(Prodotti.NomeProdotto)\
            .all()

        inventario_json = [{
            'ID_VoceInventario': v.ID_VoceInventario,
            'NomeProdotto': v.NomeProdotto,
            'Quantita': float(v.Quantita) if v.Quantita is not None else None, # Converti Decimal in float
            'UnitaMisura': v.UnitaMisura,
            'DataScadenza': v.DataScadenza.isoformat() if v.DataScadenza else None,
            'DataInserimento': v.DataInserimento.isoformat() if v.DataInserimento else None
        } for v in voci_inventario]
        return jsonify(inventario_json), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


@app.route('/api/inventario/<int:id_voce>', methods=['PUT'])
@admin_required
def modifica_voce_inventario(id_voce):
    voce = Inventario.query.get_or_404(id_voce)
    data = request.get_json()
    try:
        voce.ID_Prodotto = data.get('ID_Prodotto', voce.ID_Prodotto)
        voce.Quantita = data.get('Quantita', voce.Quantita)
        voce.DataScadenza = data.get('DataScadenza', voce.DataScadenza)
        db.session.commit()
        return jsonify({'message': 'Voce inventario modificata'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/inventario/<int:id_voce>', methods=['DELETE'])
@admin_required
def elimina_voce_inventario(id_voce):
    voce = Inventario.query.get_or_404(id_voce)
    try:
        db.session.delete(voce)
        db.session.commit()
        return jsonify({'message': 'Voce inventario eliminata'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


@app.route('/api/inventario/carichi', methods=['POST'])
@admin_required
def aggiungi_carico_inventario():
    data = request.get_json()
    try:
        nuovo_carico = CarichiInventario(
            ID_Prodotto=data['ID_Prodotto'],
            QuantitaCaricata=data['QuantitaCaricata'],
            DataCarico=data['DataCarico'], # Assicurarsi formato YYYY-MM-DD
            Fornitore=data.get('Fornitore'),
            Note=data.get('Note'),
            ID_UtenteRegistrazione=session.get('user_id') # Traccia chi ha registrato il carico
        )
        # Aggiorna anche la tabella Inventario
        voce_inventario = Inventario.query.filter_by(ID_Prodotto=data['ID_Prodotto']).first()
        if voce_inventario:
            voce_inventario.Quantita += data['QuantitaCaricata']
            # Potrebbe essere necessario gestire DataScadenza se il carico ha una scadenza diversa
        else:
            # Se il prodotto non è ancora in inventario, crealo (o gestisci l'errore)
            # Questa logica potrebbe essere più complessa a seconda dei requisiti
            # Per ora, assumiamo che il prodotto debba esistere in Prodotti ma non necessariamente in Inventario
            # Se non esiste in Inventario, potremmo voler creare una nuova voce.
            # Tuttavia, la gestione delle scadenze multiple per lo stesso prodotto diventa complessa.
            # Una semplificazione è avere una voce per prodotto in Inventario e aggiornare quella.
            # Per una gestione più fine delle scadenze, si potrebbe avere più voci per lo stesso prodotto
            # con scadenze diverse. Lo schema attuale ha una DataScadenza per voce, quindi
            # un prodotto = una voce in inventario.
            # Questo significa che un nuovo carico aggiorna la quantità e potenzialmente la scadenza
            # della voce esistente, o crea una nuova voce se il prodotto è nuovo all'inventario.
            # Per ora, aggiungiamo una nuova voce se non esiste, altrimenti aggiorniamo.
            # Sarebbe meglio che la UI gestisca se creare nuova voce o aggiornare esistente.
             return jsonify({'message': 'Prodotto non trovato in inventario per aggiornamento. Aggiungere prima il prodotto all\'inventario.'}), 404


        db.session.add(nuovo_carico)
        db.session.commit()
        return jsonify({'message': 'Carico aggiunto e inventario aggiornato', 'id_carico': nuovo_carico.ID_Carico}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

# --- Route API per Progetti ---
@app.route('/api/progetti', methods=['POST'])
@admin_required
def aggiungi_progetto():
    data = request.get_json()
    try:
        nuovo_progetto = Progetti(
            NomeProgetto=data['NomeProgetto'],
            Descrizione=data.get('Descrizione'),
            DataInizio=data.get('DataInizio'),
            DataFine=data.get('DataFine'),
            Stato=data.get('Stato', 'Pianificato'),
            ImmagineURL=data.get('ImmagineURL')
        )
        db.session.add(nuovo_progetto)
        db.session.commit()
        return jsonify({'message': 'Progetto aggiunto con successo', 'id': nuovo_progetto.ID_Progetto}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/progetti', methods=['GET'])
# @login_required # Accesso pubblico o solo loggati? Dipende dai requisiti
def get_progetti():
    try:
        lista_progetti = Progetti.query.all()
        progetti_json = [{
            'ID_Progetto': p.ID_Progetto, 'NomeProgetto': p.NomeProgetto, 'Descrizione': p.Descrizione,
            'DataInizio': p.DataInizio.isoformat() if p.DataInizio else None,
            'DataFine': p.DataFine.isoformat() if p.DataFine else None,
            'Stato': p.Stato, 'ImmagineURL': p.ImmagineURL
        } for p in lista_progetti]
        return jsonify(progetti_json), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

# --- Route API per Attività ---
@app.route('/api/attivita', methods=['POST'])
@admin_required
def aggiungi_attivita():
    data = request.get_json()
    try:
        nuova_attivita = Attivita(
            ID_Progetto=data.get('ID_Progetto'), # Può essere NULL
            NomeAttivita=data['NomeAttivita'],
            Descrizione=data.get('Descrizione'),
            DataAttivita=data.get('DataAttivita'), # Formato YYYY-MM-DD HH:MM:SS
            Luogo=data.get('Luogo'),
            ImmagineURL=data.get('ImmagineURL')
        )
        db.session.add(nuova_attivita)
        db.session.commit()
        return jsonify({'message': 'Attività aggiunta con successo', 'id': nuova_attivita.ID_Attivita}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/attivita', methods=['GET'])
# @login_required # Accesso pubblico o solo loggati?
def get_attivita():
    try:
        lista_attivita = Attivita.query.order_by(Attivita.DataAttivita.desc()).all()
        attivita_json = [{
            'ID_Attivita': a.ID_Attivita, 'ID_Progetto': a.ID_Progetto, 'NomeAttivita': a.NomeAttivita,
            'Descrizione': a.Descrizione,
            'DataAttivita': a.DataAttivita.isoformat() if a.DataAttivita else None,
            'Luogo': a.Luogo, 'ImmagineURL': a.ImmagineURL
        } for a in lista_attivita]
        return jsonify(attivita_json), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

# --- Route API per Notizie ---
@app.route('/api/notizie', methods=['POST'])
@admin_required
def aggiungi_notizia():
    data = request.get_json()
    try:
        nuova_notizia = Notizie(
            Titolo=data['Titolo'],
            Contenuto=data['Contenuto'],
            Autore=data.get('Autore', session.get('user_id')), # Default all'utente loggato se admin
            ImmagineURL=data.get('ImmagineURL'),
            Categoria=data.get('Categoria')
        )
        db.session.add(nuova_notizia)
        db.session.commit()
        return jsonify({'message': 'Notizia aggiunta con successo', 'id': nuova_notizia.ID_Notizia}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/notizie', methods=['GET'])
# @login_required # Accesso pubblico
def get_notizie():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int) # Notizie per pagina
        lista_notizie_paginated = Notizie.query.order_by(Notizie.DataPubblicazione.desc()).paginate(page=page, per_page=per_page, error_out=False)

        notizie_json = [{
            'ID_Notizia': n.ID_Notizia, 'Titolo': n.Titolo, 'Contenuto': n.Contenuto, # Potrebbe essere un riassunto
            'DataPubblicazione': n.DataPubblicazione.isoformat() if n.DataPubblicazione else None,
            'Autore': n.Autore, 'ImmagineURL': n.ImmagineURL, 'Categoria': n.Categoria
        } for n in lista_notizie_paginated.items]

        return jsonify({
            'notizie': notizie_json,
            'total_pages': lista_notizie_paginated.pages,
            'current_page': lista_notizie_paginated.page,
            'total_items': lista_notizie_paginated.total
        }), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/notizie/<int:id_notizia>', methods=['GET'])
def get_notizia_singola(id_notizia):
    try:
        notizia = Notizie.query.get_or_404(id_notizia)
        return jsonify({
            'ID_Notizia': notizia.ID_Notizia, 'Titolo': notizia.Titolo, 'Contenuto': notizia.Contenuto,
            'DataPubblicazione': notizia.DataPubblicazione.isoformat() if notizia.DataPubblicazione else None,
            'Autore': notizia.Autore, 'ImmagineURL': notizia.ImmagineURL, 'Categoria': notizia.Categoria
        }), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


# --- Route API per Distribuzioni ---
@app.route('/api/distribuzioni', methods=['POST'])
@login_required # Volontari o Admin possono creare distribuzioni
def crea_distribuzione():
    data = request.get_json()
    try:
        nuova_distribuzione = Distribuzioni(
            ID_Famiglia=data['ID_Famiglia'],
            DataDistribuzione=data['DataDistribuzione'], # Formato YYYY-MM-DD
            Note=data.get('Note'),
            ID_VolontarioConsegna=data.get('ID_VolontarioConsegna', session.get('user_id')), # Default al volontario loggato
            Stato=data.get('Stato', 'Pianificata')
        )
        db.session.add(nuova_distribuzione)
        db.session.flush() # Per ottenere l'ID_Distribuzione prima del commit

        dettagli_prodotti = data.get('prodotti', []) # Lista di {'ID_Prodotto': x, 'QuantitaDistribuita': y}
        for item in dettagli_prodotti:
            dettaglio = DettaglioDistribuzione(
                ID_Distribuzione=nuova_distribuzione.ID_Distribuzione,
                ID_Prodotto=item['ID_Prodotto'],
                QuantitaDistribuita=item['QuantitaDistribuita']
            )
            db.session.add(dettaglio)
            # Qui si dovrebbe anche scalare la quantità dall'inventario
            voce_inventario = Inventario.query.filter_by(ID_Prodotto=item['ID_Prodotto']).first()
            if voce_inventario and voce_inventario.Quantita >= item['QuantitaDistribuita']:
                voce_inventario.Quantita -= item['QuantitaDistribuita']
            else:
                # Gestire caso di quantità non sufficiente
                db.session.rollback()
                return jsonify({'message': f"Quantità non sufficiente per il prodotto ID {item['ID_Prodotto']}"}), 400

        db.session.commit()
        return jsonify({'message': 'Distribuzione creata con successo', 'id': nuova_distribuzione.ID_Distribuzione}), 201
    except KeyError as e:
        db.session.rollback()
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/distribuzioni', methods=['GET'])
@login_required
def get_distribuzioni():
    try:
        # Filtri opzionali (es. per data, per famiglia, per stato)
        mese = request.args.get('mese') # Formato YYYY-MM
        id_famiglia = request.args.get('id_famiglia', type=int)

        query = Distribuzioni.query.join(Famiglie, Distribuzioni.ID_Famiglia == Famiglie.ID_Famiglia)\
                                 .outerjoin(Utenti, Distribuzioni.ID_VolontarioConsegna == Utenti.ID_Utente)\
                                 .add_columns(
                                     Distribuzioni.ID_Distribuzione,
                                     Famiglie.NomeFamiglia.label("NomeDestinatario"),
                                     Distribuzioni.DataDistribuzione,
                                     Distribuzioni.Stato,
                                     Utenti.Nome.label("NomeVolontario"),
                                     Utenti.Cognome.label("CognomeVolontario")
                                 )

        if mese:
            # Dovrai parsare mese per ottenere anno e mese e filtrare DataDistribuzione
            pass # Implementare logica filtro per mese
        if id_famiglia:
            query = query.filter(Distribuzioni.ID_Famiglia == id_famiglia)

        lista_distribuzioni = query.order_by(Distribuzioni.DataDistribuzione.desc()).all()

        distribuzioni_json = []
        for d in lista_distribuzioni:
            distribuzioni_json.append({
                'ID_Distribuzione': d.ID_Distribuzione,
                'Destinatario': d.NomeDestinatario,
                'DataDistribuzione': d.DataDistribuzione.isoformat() if d.DataDistribuzione else None,
                'Volontario': f"{d.NomeVolontario} {d.CognomeVolontario}" if d.NomeVolontario else "N/A",
                'Stato': d.Stato,
                # Aggiungere dettagli prodotti se necessario qui
            })
        return jsonify(distribuzioni_json), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


# --- Route API per Appuntamenti (semplificato) ---
@app.route('/api/appuntamenti', methods=['POST'])
@login_required
def crea_appuntamento():
    data = request.get_json()
    try:
        nuovo_appuntamento = Appuntamenti(
            ID_Famiglia=data.get('ID_Famiglia'),
            ID_Attivita=data.get('ID_Attivita'),
            Titolo=data.get('Titolo'),
            DataOraAppuntamento=data['DataOraAppuntamento'], # YYYY-MM-DD HH:MM:SS
            Luogo=data.get('Luogo'),
            Note=data.get('Note'),
            Stato=data.get('Stato', 'Pianificato')
        )
        db.session.add(nuovo_appuntamento)
        db.session.commit()
        return jsonify({'message': 'Appuntamento creato', 'id': nuovo_appuntamento.ID_Appuntamento}), 201
    except KeyError as e:
        return jsonify({'message': f'Campo mancante: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500

@app.route('/api/appuntamenti', methods=['GET'])
@login_required
def get_appuntamenti():
    try:
        # Filtri per data, famiglia, ecc.
        mese_anno = request.args.get('mese_anno') # Es. 2024-03
        appuntamenti_list = []
        query = Appuntamenti.query
        if mese_anno:
            from datetime import datetime
            try:
                start_date = datetime.strptime(mese_anno + "-01", "%Y-%m-%d")
                import calendar
                last_day = calendar.monthrange(start_date.year, start_date.month)[1]
                end_date = datetime.strptime(mese_anno + f"-{last_day}", "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                query = query.filter(Appuntamenti.DataOraAppuntamento.between(start_date, end_date))
            except ValueError:
                return jsonify({'message': 'Formato mese_anno non valido. Usare YYYY-MM'}), 400

        appuntamenti = query.order_by(Appuntamenti.DataOraAppuntamento).all()

        for app in appuntamenti:
            app_data = {
                'ID_Appuntamento': app.ID_Appuntamento,
                'Titolo': app.Titolo,
                'DataOraAppuntamento': app.DataOraAppuntamento.isoformat() if app.DataOraAppuntamento else None,
                'Luogo': app.Luogo,
                'Note': app.Note,
                'Stato': app.Stato
            }
            if app.ID_Famiglia:
                fam = Famiglie.query.get(app.ID_Famiglia)
                app_data['NomeFamiglia'] = fam.NomeFamiglia if fam else None
            appuntamenti_list.append(app_data)

        return jsonify(appuntamenti_list), 200
    except Exception as e:
        return jsonify({'message': f'Errore del server: {str(e)}'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea le tabelle se non esistono
    app.run(debug=True) # debug=True solo per sviluppo!
