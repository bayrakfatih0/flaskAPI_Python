import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('nlp_sorulari.db')
    conn.row_factory = sqlite3.Row
    return conn

conn = sqlite3.connect('nlp_sorulari.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS sorular
    (id INTEGER PRIMARY KEY, soru TEXT, tip TEXT, cevap_a TEXT, cevap_b TEXT, cevap_c TEXT, cevap_d TEXT, dogru_cevap TEXT)
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS puanlar
    (id INTEGER PRIMARY KEY, puan INTEGER)
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS cevaplar
    (id INTEGER PRIMARY KEY, soru_id INTEGER, cevap TEXT, dogru_mu INTEGER)
''')

c.execute('DELETE FROM sorular')

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


conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html', sorular=sorular)

@app.route('/puanlar', methods=['GET'])
def get_best_score():
    conn = sqlite3.connect('nlp_sorulari.db') 
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(puan) FROM puanlar") 
    result = cursor.fetchone()
    best_score = result[0] if result[0] is not None else 0  
    conn.close()
    return jsonify({"best_score": best_score})

@app.route('/cevapla', methods=['POST'])
def cevapla():
    conn = get_db()
    c = conn.cursor()
    
    data = request.get_json()
    puan = 0
    
    c.execute('SELECT * FROM sorular')
    sorular = c.fetchall()
    
    for soru in sorular:
        cevap = data.get(f'cevap-{soru["id"]}')
        if cevap == soru['dogru_cevap']:
            puan += 20
            
        c.execute('''
            INSERT INTO cevaplar (soru_id, cevap, dogru_mu)
            VALUES (?, ?, ?)
        ''', (soru['id'], cevap, 1 if cevap == soru['dogru_cevap'] else 0))
    
    c.execute('INSERT INTO puanlar (puan) VALUES (?)', (puan,))
    conn.commit()  
    
    return jsonify({'puan': puan})

@app.route('/yeni_sinav')
def yeni_sinav():
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM cevaplar') 
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
