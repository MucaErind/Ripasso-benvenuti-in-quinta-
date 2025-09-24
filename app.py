import json
from flask import Flask, jsonify, request, redirect, url_for, flash, get_flashed_messages

# ==============================================================================
# 1. CLASSE DISTRIBUTORE E DATI INIZIALI
# ==============================================================================

class Distributore:
    """Rappresenta un singolo distributore con tutte le sue informazioni."""
    def __init__(self, id, nome, indirizzo, citta, provincia, lat, lon, livello_benzina, capacita_benzina, livello_diesel, capacita_diesel, prezzo_benzina, prezzo_diesel):
        self.id = id
        self.nome = nome
        self.indirizzo = indirizzo
        self.citta = citta
        self.provincia = provincia
        self.lat = lat
        self.lon = lon
        self.livello_benzina = livello_benzina
        self.capacita_benzina = capacita_benzina
        self.livello_diesel = livello_diesel
        self.capacita_diesel = capacita_diesel
        self.prezzo_benzina = prezzo_benzina
        self.prezzo_diesel = prezzo_diesel

    def to_dict(self):
        """Converte l'oggetto Distributore in un dizionario per le risposte API."""
        return self.__dict__

# Lista in memoria che funge da database
distributori = [
    Distributore(1, "Iperstaroil Milano", "Via Roma 1", "Milano", "MI", 45.4642, 9.1900, 5000, 10000, 8000, 15000, 1.85, 1.75),
    Distributore(2, "Iperstaroil Roma", "Piazza del Popolo 10", "Roma", "RM", 41.9109, 12.4768, 7500, 12000, 9000, 12000, 1.89, 1.79),
    Distributore(3, "Iperstaroil Napoli", "Via Toledo 15", "Napoli", "NA", 40.8399, 14.2522, 4000, 9000, 6000, 10000, 1.82, 1.72),
    Distributore(4, "Iperstaroil Torino", "Corso Vittorio Emanuele II 50", "Torino", "TO", 45.0678, 7.6745, 9000, 15000, 11000, 16000, 1.86, 1.76),
    Distributore(5, "Iperstaroil Milano Sud", "Viale Lombardia 20", "Milano", "MI", 45.4431, 9.2218, 6000, 10000, 7000, 13000, 1.84, 1.74)
]

# ==============================================================================
# 2. CREAZIONE DELL'APPLICAZIONE FLASK
# ==============================================================================

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_per_i_messaggi'

# ==============================================================================
# 3. ROTTE API (per la gestione dei dati)
# ==============================================================================

@app.route('/api/distributori', methods=['GET'])
def get_distributori():
    """API 0: Ritorna l'elenco ordinato di tutti i distributori."""
    distributori_ordinati = sorted(distributori, key=lambda d: d.id)
    return jsonify([d.to_dict() for d in distributori_ordinati])

@app.route('/api/livello/provincia/<string:provincia>', methods=['GET'])
def get_livello_provincia(provincia):
    """API 1: Ritorna i livelli dei distributori di una provincia."""
    risultato = [d.to_dict() for d in distributori if d.provincia.lower() == provincia.lower()]
    return jsonify(risultato)

@app.route('/api/livello/distributore/<int:distributore_id>', methods=['GET'])
def get_livello_distributore(distributore_id):
    """API 2: Ritorna i livelli di un distributore specifico."""
    distributore = next((d for d in distributori if d.id == distributore_id), None)
    return jsonify(distributore.to_dict()) if distributore else (jsonify({"errore": "Distributore non trovato"}), 404)

@app.route('/api/prezzo/provincia/<string:provincia>', methods=['POST'])
def set_prezzo_provincia(provincia):
    """API per modificare il prezzo per provincia."""
    data = request.get_json()
    modificati = 0
    for d in distributori:
        if d.provincia.lower() == provincia.lower():
            if 'prezzo_benzina' in data and data['prezzo_benzina']:
                d.prezzo_benzina = float(data['prezzo_benzina'])
            if 'prezzo_diesel' in data and data['prezzo_diesel']:
                d.prezzo_diesel = float(data['prezzo_diesel'])
            modificati += 1
    return jsonify({"messaggio": f"Prezzi aggiornati per {modificati} distributori."})

# ==============================================================================
# 4. ROTTE WEB (per l'interfaccia utente)
# ==============================================================================

@app.route('/', methods=['GET'])
def home():
    """Pagina principale che mostra mappa, elenco e form."""
    
    # Prepara i dati per l'HTML
    dati_distributori = [d.to_dict() for d in distributori]
    province = sorted(list(set(d.provincia for d in distributori)))
    
    # Genera dinamicamente le opzioni del menu a tendina per le province
    opzioni_province = "".join([f'<option value="{p}">{p}</option>' for p in province])
    
    # Genera dinamicamente la lista dei distributori
    lista_html = "".join([f'''
        <li class="list-group-item">
            <b>{d.id}. {d.nome} ({d.provincia})</b><br>
            <small>
                Benzina: {d.prezzo_benzina:.3f}€ - Liv: {d.livello_benzina}L<br>
                Diesel: {d.prezzo_diesel:.3f}€ - Liv: {d.livello_diesel}L
            </small>
        </li>
    ''' for d in distributori])

    # Ottieni i messaggi flash (se presenti)
    flashed_messages = get_flashed_messages(with_categories=True)
    alert_html = ""
    if flashed_messages:
        for category, message in flashed_messages:
            alert_html += f'<div class="alert alert-{category}">{message}</div>'

    # Incorpora l'HTML in una stringa
    html_content = f'''
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Monitor Iperstaroil</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <style> #map {{ height: 600px; }} </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="mb-4 text-center">Dashboard Monitoraggio Iperstaroil ⛽</h1>
            {alert_html}
            <div class="row">
                <div class="col-md-8">
                    <div class="card shadow-sm">
                        <div class="card-header"><h3>Mappa Distributori</h3></div>
                        <div class="card-body"><div id="map"></div></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card shadow-sm mb-4">
                        <div class="card-header"><h3>Cambia Prezzi per Provincia</h3></div>
                        <div class="card-body">
                            <form action="/cambia-prezzo" method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Provincia</label>
                                    <select name="provincia" class="form-select">{opzioni_province}</select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Nuovo Prezzo Benzina</label>
                                    <input type="number" step="0.001" name="prezzo_benzina" class="form-control" placeholder="es. 1.850">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Nuovo Prezzo Diesel</label>
                                    <input type="number" step="0.001" name="prezzo_diesel" class="form-control" placeholder="es. 1.750">
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Applica Modifiche</button>
                            </form>
                        </div>
                    </div>
                    <div class="card shadow-sm">
                        <div class="card-header"><h3>Elenco Distributori</h3></div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            <ul class="list-group list-group-flush">{lista_html}</ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([41.9, 12.5], 5.5);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            var distributori = {json.dumps(dati_distributori)};
            distributori.forEach(d => {{
                L.marker([d.lat, d.lon]).addTo(map)
                    .bindPopup(`<b>${{d.nome}}</b><br>Benzina: ${{d.prezzo_benzina.toFixed(3)}}€<br>Diesel: ${{d.prezzo_diesel.toFixed(3)}}€`);
            }});
        </script>
    </body>
    </html>
    '''
    return html_content

@app.route('/cambia-prezzo', methods=['POST'])
def cambia_prezzo_web():
    """Riceve i dati dal form web e chiama l'API interna per la modifica."""
    provincia = request.form.get('provincia')
    prezzo_benzina = request.form.get('prezzo_benzina')
    prezzo_diesel = request.form.get('prezzo_diesel')
    
    payload = {}
    if prezzo_benzina: payload['prezzo_benzina'] = prezzo_benzina
    if prezzo_diesel: payload['prezzo_diesel'] = prezzo_diesel

    if not payload:
        flash("Nessun nuovo prezzo inserito. Nessuna modifica effettuata.", "warning")
    else:
        # In un'architettura reale, qui si farebbe una richiesta a un altro servizio.
        # Qui simuliamo la chiamata diretta alla funzione API per semplicità.
        with app.test_request_context(f'/api/prezzo/provincia/{provincia}', method='POST', json=payload):
            set_prezzo_provincia(provincia)
        flash(f"Prezzi per la provincia di {provincia} aggiornati con successo!", "success")

    return redirect(url_for('home'))

# ==============================================================================
# 5. ESECUZIONE DELL'APPLICAZIONE
# ==============================================================================

if __name__ == '__main__':
    print("=====================================================")
    print("🚀 Server Iperstaroil in esecuzione!")
    print("🔗 Apri il browser e vai a: http://127.0.0.1:5000")
    print("=====================================================")
    app.run(debug=True, port=5000)