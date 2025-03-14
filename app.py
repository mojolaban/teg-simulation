from flask import Flask, redirect, render_template, request, jsonify, url_for, Response
from database import engine, insert_group_treatment, fetch_init_data, retrieve_data, insert_demog, insert_group_lang
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
import json
import random
import os

app = Flask(__name__)
app.url_map.strict_slashes = False

# API endpoint for game data
@app.route("/sendData", methods=['POST'])
def send_games_data():
    data = request.get_json()
    timer_value = data.get('timerValue')
    lang = data.get('lang')
    price_value = int(data.get('priceValue', '0').replace(',', '').replace('.', '')) or 0
    user_id = data.get('userid', '').strip()
    group_id = data.get('groupid', '').strip()
    pos_value_str = data.get('posValue', '').strip()
    pos_value = {'JUAL': 'b', 'BELI': 's'}.get(pos_value_str, pos_value_str)

    # Helper function to safely convert to int, handling strings and numbers
    def to_int(value, default=0):
        if isinstance(value, str):
            return int(value.replace(',', '').replace('.', '')) if value.strip() else default
        return int(value) if value is not None else default

    # Helper function to keep floats for crypto fields
    def safe_float(value, default=0.0):
        if isinstance(value, str):
            return float(value.replace(',', '.').strip()) if value.strip() else default
        return float(value) if value is not None else default

    params = {
        "sec": timer_value,
        "price": price_value,
        "id": user_id,
        "gr": group_id,
        "pos": pos_value,
        "trx": to_int(data.get('trxValue')),
        "round": to_int(data.get('roundValue')),
        "crypto_prev": safe_float(data.get('cryptoPrevValue')),
        "fiat_prev": to_int(data.get('fiatPrevValue')),
        "crypto": safe_float(data.get('cryptoValue')),
        "fiat": to_int(data.get('fiatValue')),
        "buy_prev": to_int(data.get('buyPrevValue')),
        "buy": to_int(data.get('buyValue')),
        "sell": to_int(data.get('sellValue')),
        "t_gain": to_int(data.get('tGainValue')),
        "t_tax": to_int(data.get('tTaxValue')),
        "t_gain_net": to_int(data.get('tGainNetValue')),
        "r_gain": to_int(data.get('rGainValue')),
        "r_gain_prev": to_int(data.get('rGainPrevValue')),
        "r_tax": to_int(data.get('rTaxValue')),
        "r_tax_prev": to_int(data.get('rTaxPrevValue')),
        "r_gain_net": to_int(data.get('rGainNetValue')),
        "tax_disclos": to_int(data.get('taxDisclosValue')),
        "audit": to_int(data.get('auditValue')),
        "lang": lang
    }

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO responses (sec, price, id, gr, pos, trx, round, crypto_prev, fiat_prev,
                crypto, fiat, buy_prev, buy, sell, t_gain, t_tax, t_gain_net, r_gain, r_gain_prev,
                r_tax, r_tax_prev, r_gain_net, tax_disclos, audit, lang)
                VALUES (:sec, :price, :id, :gr, :pos, :trx, :round, :crypto_prev, :fiat_prev, :crypto,
                :fiat, :buy_prev, :buy, :sell, :t_gain, :t_tax, :t_gain_net, :r_gain, :r_gain_prev,
                :r_tax, :r_tax_prev, :r_gain_net, :tax_disclos, :audit, :lang)
            """),
            params
        )
        conn.commit()  # Ensure the transaction is committed
        result = conn.execute(
            text("""
                SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, 
                crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, 
                r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, lang 
                FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1
            """),
            {"id": user_id}
        )
        row = result.fetchone()
        if row:
            data = dict(row._mapping)
            lang = data['lang']
            asset_type = {
                ('2', 0): "Crypto", ('2', 1): "Kripto",
                ('1', 0): "Stock", ('1', 1): "Saham"
            }.get((data['gr'], lang), "Unknown")
            pos_map = {
                's': {0: "SELL", 1: "JUAL"},
                'b': {0: "BUY", 1: "BELI"}
            }
            data['pos'] = pos_map.get(data['pos'], {}).get(lang, data['pos']) if data['trx'] < 5 else "STOP"
            data['asset_type'] = asset_type
            # Ensure Fiat values are returned as whole numbers
            for key in ['fiat', 'fiat_prev', 'buy', 'buy_prev', 'sell', 't_gain', 't_tax', 't_gain_net', 
                        'r_gain', 'r_gain_prev', 'r_tax', 'r_tax_prev', 'r_gain_net', 'tax_disclos', 
                        'tax_discre', 'penalty', 'r_gain_final', 'price']:
                if key in data:
                    data[key] = int(data[key])
            return jsonify(data)

# Main route for page navigation
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'language' in request.form:
            treatment_dict = insert_group_lang(request.form['language'])
            print(f"DEBUG: Language selected, treatment_dict={treatment_dict}")
            return render_template('home-a.html', id=treatment_dict["id"], treatment=treatment_dict["treatment"], 
                                 lang=treatment_dict["lang"], au=treatment_dict["au"])

        elif 'form_type' in request.form:
            form_type = request.form['form_type']
            id = request.form.get('id')
            treatment = request.form.get('treatment')
            lang = request.form.get('lang')
            au = request.form.get('au')

            if form_type == 'home':
                print(f"DEBUG: Moving to demographic form with id={id}")
                return render_template('form_demog-a.html', id=id, treatment=treatment, lang=lang, au=au)

            elif form_type == 'demographic':
                print(f"DEBUG: Inserting demographic data for id={id}")
                insert_demog(
                    request.form.get('gender'), request.form.get('age'), request.form.get('education_level'),
                    request.form.get('current_education'), request.form.get('country_residence', 'indonesia'),
                    request.form.get('citizenship', 'indonesia'), ','.join(request.form.getlist('asset_experience[]')),
                    request.form.get('tax_experience'), request.form.get('description'), id
                )
                if treatment == "1":
                    return render_template('instruction-1-a.html', id=id, asset_type='stock', lang=lang, au=au)
                elif treatment == "2":
                    return render_template('instruction-2-a.html', id=id, asset_type='crypto', lang=lang, au=au)

            elif form_type == 'instruction':
                asset_type = request.form.get('asset_type')
                gr = "1" if asset_type == "stock" else "2" if asset_type == "crypto" else "unknown"
                print(f"DEBUG: Inserting treatment with id={id}, gr={gr}, lang={lang}")
                insert_group_treatment(gr, id, lang)
                templates = {
                    ("stock", "0"): 'instruction-tryout-1.html',
                    ("stock", "1"): 'instruction-tryout-1-a.html',
                    ("crypto", "0"): 'instruction-tryout-2.html',
                    ("crypto", "1"): 'instruction-tryout-2-a.html'
                }
                return render_template(templates.get((asset_type, lang), 'index.html'), id=id, asset_type=asset_type, lang=lang)

            elif form_type == 'start':
                print(f"DEBUG: Starting with id={id}, lang={lang}")
                init_data = fetch_init_data(id)
                print(f"DEBUG: init_data={init_data}")
                if init_data:
                    return render_template('round0.html' if lang == "0" else 'round0-a.html', data=init_data)
                return "Error: Invalid ID"

            elif form_type == 'tryout':
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT round, gr FROM responses WHERE id = :user_id ORDER BY ts DESC LIMIT 1"),
                        {"user_id": id}
                    )
                    latest_round, gr = result.fetchone()
                    if latest_round < 15:
                        next_round = latest_round + 1
                        conn.execute(
                            text("""
                                INSERT INTO responses (round, gr, id, trx, crypto, fiat, buy, sell, pos, 
                                t_gain, r_gain, t_tax, tax_disclos, audit, t_gain_net, r_gain_net, r_tax, 
                                sec, price, crypto_prev, fiat_prev, buy_prev, r_gain_prev, r_tax_prev, lang)
                                VALUES (:round, :gr, :id, :trx, :crypto, :fiat, :buy, :sell, :pos, :t_gain, 
                                :r_gain, :t_tax, :tax_disclos, :audit, :t_gain_net, :r_gain_net, :r_tax, 
                                :sec, :price, :crypto_prev, :fiat_prev, :buy_prev, :r_gain_prev, :r_tax_prev, :lang)
                            """),
                            {"round": next_round, "gr": gr, "id": id, "trx": 0, "crypto": 1.00, "fiat": 0,
                             "buy": 0, "sell": 0, "pos": 's', "t_gain": 0, "r_gain": 0, "t_tax": 0,
                             "tax_disclos": 0, "audit": 0, "t_gain_net": 0, "r_gain_net": 0, "r_tax": 0,
                             "sec": 0, "price": 0, "crypto_prev": 0, "fiat_prev": 0, "buy_prev": 0,
                             "r_gain_prev": 0, "r_tax_prev": 0, "lang": lang}
                        )
                        conn.commit()  # Commit the transaction
                        init_data = fetch_init_data(id)
                        if init_data:
                            return render_template('rounds.html' if lang == '0' else 'rounds-a.html', data=init_data)

            elif form_type == 'tax_reporting':
                response = retrieve_data(id)
                response_data = response.json
                template_name = 'tax_reporting-a.html' if response_data['lang'] == 1 else 'tax_reporting.html'
                if 'lang' in response_data and response_data['lang'] in [0, 1]:
                    return render_template(template_name, summary_data=response_data)
                return "Error: Invalid ID"

            elif form_type == 'tax_disclosure':
                taxdisclos = request.form.get('tax_disclos', '').replace('.', '') if lang == '1' else request.form.get('tax_disclos', '').replace(',', '')
                audit_value = 0 if random.random() < 0.8 else 1

                if not id or not lang or taxdisclos is None:
                    return "Missing data", 400

                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            UPDATE responses 
                            SET tax_disclos = :tax_disclos, audit = :audit 
                            WHERE id = :user_id 
                            AND ts = (SELECT MAX(ts) FROM responses WHERE id = :user_id)
                        """),
                        {"tax_disclos": taxdisclos, "audit": audit_value, "user_id": id}
                    )
                    conn.commit()  # Commit the transaction
                    result = conn.execute(
                        text("SELECT round, audit FROM responses WHERE id = :user_id ORDER BY ts DESC LIMIT 1"),
                        {"user_id": id}
                    )
                    latest_round, latest_audit = result.fetchone()

                template_name = f"tax_audit_{'1' if latest_audit == 1 else '0'}{'-a' if lang == '1' else ''}.html"
                response_data = retrieve_data(id).json
                return render_template(template_name, summary_data=response_data)

            elif form_type == 'next_round':
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT round, gr FROM responses WHERE id = :user_id ORDER BY ts DESC LIMIT 1"),
                        {"user_id": id}
                    )
                    latest_round, gr = result.fetchone()

                    if latest_round < 15:
                        next_round = latest_round + 1
                        conn.execute(
                            text("""
                                INSERT INTO responses (round, gr, id, trx, crypto, fiat, buy, sell, pos, 
                                t_gain, r_gain, t_tax, tax_disclos, audit, t_gain_net, r_gain_net, r_tax, 
                                sec, price, crypto_prev, fiat_prev, buy_prev, r_gain_prev, r_tax_prev, lang)
                                VALUES (:round, :gr, :id, :trx, :crypto, :fiat, :buy, :sell, :pos, :t_gain, 
                                :r_gain, :t_tax, :tax_disclos, :audit, :t_gain_net, :r_gain_net, :r_tax, 
                                :sec, :price, :crypto_prev, :fiat_prev, :buy_prev, :r_gain_prev, :r_tax_prev, :lang)
                            """),
                            {"round": next_round, "gr": gr, "id": id, "trx": 0, "crypto": 1.00, "fiat": 0,
                             "buy": 0, "sell": 0, "pos": 's', "t_gain": 0, "r_gain": 0, "t_tax": 0,
                             "tax_disclos": 0, "audit": 0, "t_gain_net": 0, "r_gain_net": 0, "r_tax": 0,
                             "sec": 0, "price": 0, "crypto_prev": 0, "fiat_prev": 0, "buy_prev": 0,
                             "r_gain_prev": 0, "r_tax_prev": 0, "lang": lang}
                        )
                        conn.commit()  # Commit the transaction
                        init_data = fetch_init_data(id)
                        if init_data:
                            return render_template('rounds.html' if lang == '0' else 'rounds-a.html', data=init_data)
                    else:
                        random_number = random.randint(1, 15)
                        result = conn.execute(
                            text("""
                                SELECT id, gr, round, r_gain_final, lang FROM responses 
                                WHERE id = :user_id AND round = :round ORDER BY ts DESC LIMIT 1
                            """),
                            {"user_id": id, "round": random_number}
                        )
                        row = result.fetchone()
                        if row:
                            user_id, gr, comp_round, comp_amt, lang = row
                            comp_rgainfinal = {
                                0: {True: 5, False: 100000},
                                1: {True: 10, False: 150000},
                                2: {True: 20, False: 250000}
                            }.get(
                                0 if comp_amt < 1000000 else 1 if comp_amt <= 5000000 else 2,
                                {True: 0, False: 0}
                            )[lang == 0]
                            template = "the_random_picker.html" if lang == 0 else "the_random_picker-a.html"
                            return render_template(template, user_id=user_id, comp_round=comp_round, 
                                                 comp_amt=comp_amt, comp_rgainfinal=comp_rgainfinal, gr=gr, lang=lang)
                        return "No data found"

            elif form_type == 'survey':
                id, gr, lang = request.form.get('id'), request.form.get('gr'), request.form.get('lang')
                comp_amt, comp_round, comp_rgainfinal = (request.form.get(k) for k in ('comp_amt', 'comp_round', 'comp_rgainfinal'))
                if not all([id, gr, lang]):
                    return "Missing required data", 400

                if comp_amt and comp_round and comp_rgainfinal:
                    with engine.connect() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO compensation (comp_amt, id, comp_round, comp_rgainfinal, gr, lang)
                                VALUES (:comp_amt, :id, :comp_round, :comp_rgainfinal, :gr, :lang)
                            """),
                            {"comp_amt": comp_amt, "id": id, "comp_round": comp_round, 
                             "comp_rgainfinal": comp_rgainfinal, "gr": gr[:1], "lang": lang}
                        )
                        conn.commit()  # Commit the transaction

                questions = [
                    '... because to me it’s obvious that this is what you do.',
                    '... even if tax audits did not exist.',
                    '... without spending a long time thinking how I could reduce them.',
                    'I feel that I am forced to pay my crypto taxes.',
                    'I pay my crypto taxes because the risk of being checked is too high.',
                    'I pay my crypto taxes for I don`t know how to evade taxes without attracting attention.',
                    'Tax officers pass information in an understandable way.',
                    'Tax officers know exactly how a correct crypto tax report should look like.',
                    'Tax officers inform and advise taxpayers how to pay crypto taxes correctly.',
                    'Tax officers have the legal right to collect crypto taxes.',
                    'Tax officers apply severe punishments.',
                    'Tax officers prosecute taxpayers mainly with audits and fines.',
                    'Tax officers enforce compliance through audits and fines.',
                    'I trust tax officers without thinking about it.',
                    'I trust tax officers automatically.',
                    'I trust tax officers usually without dealing with it deeply.',
                    'I trust the tax officers because the political and economic situation enables them to work professionally.',
                    'I trust the tax officers because they accomplish their work very well and competently.',
                    'I trust the tax officers because they are benevolent to taxpayers.',
                    'I trust the tax officers because the tax officers pursue important goals for the country.',
                    'Most other taxpayers are paying their taxes correctly without thinking about it.',
                    'Most other taxpayers automatically pay their taxes.',
                    'Most other taxpayers pay their crypto taxes honestly without dealing with it deeply.',
                    'Most other taxpayers pay their crypto taxes honestly because of audits and fines.',
                    'Most other taxpayers pay their crypto taxes honestly because they respect the law.',
                    'Most other taxpayers pay their crypto taxes honestly because they love their country.',
                    'Most other taxpayers pay crypto taxes because they get something in exchange.',
                    'Most other taxpayers pay crypto taxes because taxes are used for public interests such as education & health.',
                    'Most other taxpayers pay crypto taxes because its a way to close the gap between rich and poor.',
                    'I trust the crypto-intermediaries without thinking about it.',
                    'I trust the crypto-intermediaries automatically.',
                    'I trust crypto-intermediaries usually without dealing with it deeply.',
                    'I trust crypto intermediaries because the regulatory environment allows them to operate transparently and professionally.',
                    'I trust crypto intermediaries because they execute transactions efficiently and competently.',
                    "I trust crypto intermediaries because they demonstrate a commitment to protecting their users' interests.",
                    'I trust crypto intermediaries because they are aligned with important goals, such as enhancing financial security and innovation.',
                    'How likely will you pay your crypto taxes for the current year correctly and in full extent to the tax authority?'
                ]

                questindo = [
                    '... karena bagi saya jelas ini yang harus saya lakukan.',
                    '... bahkan jika audit pajak tidak ada.',
                    '... tanpa menghabiskan waktu lama memikirkan bagaimana saya bisa menguranginya.',
                    'Saya merasa bahwa saya dipaksa untuk membayar pajak.',
                    'Saya membayar pajak karena risiko diaudit terlalu tinggi.',
                    'Saya membayar pajak karena saya tidak tahu cara menghindari pajak tanpa menarik perhatian.',
                    'Petugas pajak menyampaikan informasi dengan cara yang mudah dipahami.',
                    'Petugas pajak tahu persis bagaimana seharusnya laporan pajak yang benar.',
                    'Petugas pajak menginformasikan dan menasihati wajib pajak cara membayar pajak dengan benar.',
                    'Petugas pajak memiliki mandat hukum untuk mengumpulkan pajak.',
                    'Petugas pajak menerapkan hukuman yang berat.',
                    'Petugas pajak memprosekusi wajib pajak terutama dengan audit dan denda.',
                    'Petugas pajak memaksa wajib pajak patuh melalui audit dan denda.',
                    'Saya mempercayai petugas pajak tanpa berpikir panjang.',
                    'Saya secara otomatis mempercayai petugas pajak.',
                    'Biasanya saya mempercayai petugas pajak tanpa memikirkannya secara mendalam.',
                    'Saya mempercayai petugas pajak karena situasi politik dan ekonomi memungkinkan mereka bekerja secara profesional.',
                    'Saya mempercayai petugas pajak karena mereka melakukan pekerjaan mereka dengan sangat baik dan kompeten.',
                    'Saya mempercayai petugas pajak karena mereka memiliki niatan baik kepada wajib pajak.',
                    'Saya mempercayai petugas pajak karena petugas pajak bekerja untuk mencapai tujuan penting bernegara.',
                    'Sebagian besar wajib pajak lain membayar pajak mereka dengan benar tanpa memikirkannya.',
                    'Sebagian besar wajib pajak lain secara otomatis membayar pajak mereka.',
                    'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur tanpa memikirkannya secara mendalam.',
                    'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur karena audit dan denda.',
                    'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur karena mereka menghormati hukum.',
                    'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur karena mereka mencintai negaranya.',
                    'Sebagian besar wajib pajak lain membayar pajak karena mereka mendapatkan sesuatu sebagai imbalannya.',
                    'Sebagian besar wajib pajak lain membayar pajak karena pajak digunakan untuk kepentingan publik seperti pendidikan & kesehatan.',
                    'Sebagian besar wajib pajak lain membayar pajak sebagai cara untuk menutup kesenjangan antara kaya dan miskin.',
                    'Saya percaya kepada para perantara kripto tanpa berpikir panjang.',
                    'Saya secara otomatis mempercayai para perantara kripto.',
                    'Saya biasanya percaya kepada perantara kripto tanpa memikirkannya secara mendalam.',
                    'Saya percaya kepada perantara kripto karena lingkungan regulasi memungkinkan mereka beroperasi secara transparan dan profesional.',
                    'Saya percaya kepada perantara kripto karena mereka mengeksekusi transaksi secara efisien dan kompeten.',
                    'Saya percaya kepada perantara kripto karena mereka menunjukkan komitmen untuk melindungi kepentingan penggunanya.',
                    'Saya percaya kepada perantara kripto karena visi mereka selaras dengan tujuan-tujuan penting, seperti meningkatkan keamanan keuangan dan inovasi.',
                    'Seberapa mungkin Anda akan membayar pajak kripto Anda untuk tahun ini secara benar dan penuh kepada otoritas pajak?'
                ]

                return render_template('the_survey.html' if lang == '0' else 'the_survey-a.html', 
                                     id=id, gr=gr, lang=lang, questions=questions if lang == '0' else questindo)

            elif form_type == 'survey_end':
                form_data = dict(request.form)
                insert_values = {
                    k: form_data.get(k) for k in 
                    [f'question{i}' for i in range(37)] + 
                    ['email', 'gr', 'id', 'comments', 'followup', 'lang', 'veteran', 'cryptorisk', 'trustpower', 'comments_a', 'comments_b']
                }

                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO survey (question0, question1, question2, question3, question4, question5, 
                            question6, question7, question8, question9, question10, question11, question12, question13, 
                            question14, question15, question16, question17, question18, question19, question20, question21, 
                            question22, question23, question24, question25, question26, question27, question28, question29, 
                            question30, question31, question32, question33, question34, question35, question36, email, gr, 
                            id, comments, followup, lang, veteran, cryptorisk, trustpower, comments_a, comments_b)
                            VALUES (:question0, :question1, :question2, :question3, :question4, :question5, :question6, 
                            :question7, :question8, :question9, :question10, :question11, :question12, :question13, 
                            :question14, :question15, :question16, :question17, :question18, :question19, :question20, 
                            :question21, :question22, :question23, :question24, :question25, :question26, :question27, 
                            :question28, :question29, :question30, :question31, :question32, :question33, :question34, 
                            :question35, :question36, :email, :gr, :id, :comments, :followup, :lang, :veteran, 
                            :cryptorisk, :trustpower, :comments_a, :comments_b)
                        """),
                        insert_values
                    )
                    conn.commit()  # Commit the transaction
                return render_template('the_survey_ends.html' if lang == '0' else 'the_survey_ends-a.html')

    return render_template('index.html')

# Jinja filter for crypto formatting
def format_crypto(value, lang):
    if isinstance(value, (Decimal, float)):
        if lang == 1:  # Indonesian
            return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
        return "{:,.2f}".format(value)
    return value

app.jinja_env.filters['format_crypto'] = format_crypto

# Test route for round0-a
@app.route('/test-round0a')
def test_round0a():
    sample_data = {
        'round': 0, 'gr': '1', 'id': 'TEST', 'trx': 0, 'crypto': '1.00', 'fiat': '0', 'buy': '0', 
        'sell': '0', 'pos': 'BELI', 't_gain': '0', 'r_gain': '0', 't_tax': '0', 'asset_type': 'Saham',
        'crypto_prev': '0', 'fiat_prev': '0', 'buy_prev': '0', 'r_tax': '0', 'r_gain_net': '0', 
        't_gain_net': '0', 'r_gain_prev': '0', 'r_tax_prev': '0', 'tax_disclos': '0', 'tax_discre': '0', 
        'audit': '0', 'penalty': '0', 'r_gain_final': '0', 'lang': 1
    }
    return render_template('round0-a.html', data=sample_data)

# Video streaming route
@app.route('/video/<filename>')
def stream_video(filename):
    def generate():
        video_path = os.path.join(app.static_folder, filename)
        with open(video_path, 'rb') as video:
            while chunk := video.read(1024 * 1024):  # 1MB chunks
                yield chunk

    return Response(
        generate(),
        mimetype='video/mp4',
        headers={'Accept-Ranges': 'bytes', 'Cache-Control': 'public, max-age=3600', 'Content-Disposition': 'inline'}
    )

# Run the application
if __name__ == "__main__":
    import sys
    port = int(os.environ.get("PORT", 3000))
    try:
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)