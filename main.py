import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('nlp_sorulari.db')
    conn.row_factory = sqlite3.Row
    return conn

# Database bağlantısı oluşturur
conn = sqlite3.connect('nlp_sorulari.db')
c = conn.cursor()

# Sorular tablosu oluşturur
c.execute('''
    CREATE TABLE IF NOT EXISTS sorular
    (id INTEGER PRIMARY KEY, soru TEXT, tip TEXT, cevap_a TEXT, cevap_b TEXT, cevap_c TEXT, cevap_d TEXT, dogru_cevap TEXT)
''')

# Cevaplar tablosu oluşturur
c.execute('''
    CREATE TABLE IF NOT EXISTS puanlar
    (id INTEGER PRIMARY KEY, puan INTEGER)
''')

# Cevaplar tablosu oluşturur
c.execute('''
    CREATE TABLE IF NOT EXISTS cevaplar
    (id INTEGER PRIMARY KEY, soru_id INTEGER, cevap TEXT, dogru_mu INTEGER)
''')

# Sorular ve puanlar tablolarını temizle
c.execute('DELETE FROM sorular')
c.execute('DELETE FROM puanlar')
c.execute('DELETE FROM cevaplar')

# Soruları database'e ekler
sorular = [
    {"id": 1, "soru": "NLP'nin temel amacı nedir?", "tip": "secenek", "cevap_a": "Doğal dil işleme", "cevap_b": "Makine öğrenmesi", "cevap_c": "Veri madenciliği", "cevap_d": "Bilgisayar görselleştirme", "dogru_cevap": "Doğal dil işleme"},
    {"id": 2, "soru": "NLP'de kullanılan temel teknikler nelerdir?", "tip": "secenek", "cevap_a": "Tokenization, stemming, lemmatization", "cevap_b": "Named entity recognition, part-of-speech tagging", "cevap_c": "Sentiment analysis, topic modeling", "cevap_d": "Tüm yukarıdakiler", "dogru_cevap": "Tüm yukarıdakiler"},
    {"id": 3, "soru": "NLP'de kullanılan popüler kütüphaneler nelerdir?", "tip": "metin", "dogru_cevap": "NLTK, spaCy"},
    {"id": 4, "soru": "NLP'de kullanılan temel algoritmalar nelerdir?", "tip": "secenek", "cevap_a": "Naive Bayes, decision trees", "cevap_b": "Random forest, support vector machines", "cevap_c": "Gradient boosting, neural networks", "cevap_d": "Tüm yukarıdakiler", "dogru_cevap": "Tüm yukarıdakiler"},
    {"id": 5, "soru": "NLP'nin uygulama alanları nelerdir?", "tip": "metin", "dogru_cevap": "Dil çevirisi, metin sınıflandırması"}
]

for soru in sorular:
    c.execute('''
        INSERT INTO sorular (id, soru, tip, cevap_a, cevap_b, cevap_c, cevap_d, dogru_cevap)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (soru['id'], soru['soru'], soru['tip'], soru.get('cevap_a', ''), soru.get('cevap_b', ''), soru.get('cevap_c', ''), soru.get('cevap_d', ''), soru['dogru_cevap']))

# Database'i kaydeder
conn.commit()

# Database bağlantısını kapatır
conn.close()

@app.route('/')
def index():
    return render_template('index.html', sorular=sorular)

@app.route('/cevapla', methods=['POST'])
def cevapla():
    conn = get_db()
    c = conn.cursor()
    
    data = request.get_json()
    puan = 0
    
    # Soruları al
    c.execute('SELECT * FROM sorular')
    sorular = c.fetchall()
    
    # Her soru için cevapları kontrol et
    for soru in sorular:
        cevap = data.get(f'cevap-{soru["id"]}')
        if cevap == soru['dogru_cevap']:
            puan += 20
            
        # Cevabı kaydet
        c.execute('''INSERT INTO cevaplar 
                    (soru_id, cevap, dogru_mu)
                    VALUES (?, ?, ?)''', 
                    (soru['id'], cevap, 1 if cevap == soru['dogru_cevap'] else 0))
    
    # Puanı kaydet
    c.execute('INSERT INTO puanlar (puan) VALUES (?)', (puan,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'puan': puan})

@app.route('/puanlar')
def puanlar():
    conn = sqlite3.connect('nlp_sorulari.db')
    c = conn.cursor()
    c.execute('SELECT * FROM puanlar')
    puanlar = c.fetchall()
    conn.close()
    return render_template('puanlar.html', puanlar=puanlar)

@app.route('/cevaplar')
def cevaplar():
    conn = sqlite3.connect('nlp_sorulari.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cevaplar')
    cevaplar = c.fetchall()
    conn.close()
    return render_template('cevaplar.html', cevaplar=cevaplar)

