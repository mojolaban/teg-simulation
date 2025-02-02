from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from database import engine, insert_group_treatment, fetch_init_data, retrieve_data, insert_demog, insert_group_lang
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
import json
import random

app = Flask(__name__)
app.url_map.strict_slashes = False


# API endpoint for game data
@app.route("/sendData", methods=['POST'])
def send_games_data():
    data = request.get_json()
    timer_value = data.get('timerValue')
    lang = data.get('lang')
    price_value = data.get('priceValue', '').replace(',', '').replace('.', '')

    if not price_value:
        price_value = 0 

    user_id = data.get('userid').replace('\n', '').strip()
    group_id = data.get('groupid').replace('\n', '').strip()
    pos_value_str = data.get('posValue', '').replace('\n', '').strip()

    if pos_value_str == "JUAL":
        pos_value = "b"
    elif pos_value_str == "BELI":
        pos_value = "s"
    else:
        pos_value = pos_value_str

    trx_value = data.get('trxValue')
    round_value = data.get('roundValue')

    crypto_prev_value_raw = data.get('cryptoPrevValue')  
    if isinstance(crypto_prev_value_raw, str):
        crypto_prev_value = crypto_prev_value_raw.replace('\n', '').strip()
    else:
        crypto_prev_value = crypto_prev_value_raw

    fiat_prev_value = data.get('fiatPrevValue')
    crypto_value_raw = data.get('cryptoValue')  
    if isinstance(crypto_value_raw, str):
        crypto_value = crypto_value_raw.replace('\n', '').strip()
    else:
        crypto_value = crypto_value_raw

    fiat_value_raw = data.get('fiatValue')  
    if isinstance(fiat_value_raw, str):
        fiat_value = fiat_value_raw.replace('\n', '').strip()
    else:
        fiat_value = fiat_value_raw

    buy_prev_value = data.get('buyPrevValue')
    sell_value_raw = data.get('sellValue')
    if isinstance(sell_value_raw, str):
        sell_value = sell_value_raw.replace('\n', '').strip()
    else:
        sell_value = sell_value_raw
    buy_value = data.get('buyValue')
    t_gain_value_raw = data.get('tGainValue')
    if isinstance(t_gain_value_raw, str):
        t_gain_value = t_gain_value_raw.replace('\n', '').strip()
    else:
        t_gain_value = t_gain_value_raw
    t_tax_value_raw = data.get('tTaxValue')
    if isinstance(t_tax_value_raw, str):
        t_tax_value = t_tax_value_raw.replace('\n', '').strip()
    else:
        t_tax_value = t_tax_value_raw

    t_gain_net_value_raw = data.get('tGainNetValue')
    if isinstance(t_gain_net_value_raw, str):
        t_gain_net_value = t_gain_net_value_raw.replace('\n', '').strip()
    else:
        t_gain_net_value = t_gain_net_value_raw
    r_gain_value = data.get('rGainValue')
    r_gain_prev_value = data.get('rGainPrevValue')
    r_tax_value = data.get('rTaxValue')
    r_tax_prev_value = data.get('rTaxPrevValue')
    r_gain_net_value = str(data.get('rGainNetValue'))
    r_gain_net_value = r_gain_net_value.replace('\n', '').strip()
    tax_disclos_value = data.get('taxDisclosValue')
    audit_value = data.get('auditValue')

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO `teg-simulation-sandbox`.`responses` 
            (`sec`,`price`,`id`, `gr`, `pos`, `trx`, `round`, `crypto_prev`, `fiat_prev`,
             `crypto`, `fiat`, `buy_prev`, `buy`, `sell`, `t_gain`,`t_tax`, `t_gain_net`, 
             `r_gain`, `r_gain_prev`, `r_tax`, `r_tax_prev`, `r_gain_net`, `tax_disclos`,
             `audit`, `lang`) 
            VALUES 
            (:sec, :price, :id, :gr, :pos, :trx, :round, :crypto_prev, :fiat_prev, :crypto, 
             :fiat, :buy_prev, :buy, :sell, :t_gain, :t_tax, :t_gain_net, :r_gain, :r_gain_prev, 
             :r_tax, :r_tax_prev, :r_gain_net, :tax_disclos, :audit, :lang)
        """), {
            "sec": timer_value, "price": price_value, "id": user_id, "gr": group_id,
            "pos": pos_value, "trx": trx_value, "round": round_value,
            "crypto_prev": crypto_prev_value, "fiat_prev": fiat_prev_value,
            "crypto": crypto_value, "fiat": fiat_value, "buy_prev": buy_prev_value,
            "buy": buy_value, "sell": sell_value, "t_gain": t_gain_value,
            "t_tax": t_tax_value, "t_gain_net": t_gain_net_value,
            "r_gain": r_gain_value, "r_gain_prev": r_gain_prev_value,
            "r_tax": r_tax_value, "r_tax_prev": r_tax_prev_value,
            "r_gain_net": r_gain_net_value, "tax_disclos": tax_disclos_value,
            "audit": audit_value, "lang": lang
        })

        result = conn.execute(text("""
            SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, 
                   t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, 
                   r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, 
                   r_gain_final, lang 
            FROM responses 
            WHERE id = :id 
            ORDER BY ts DESC 
            LIMIT 1;
        """), {"id": user_id})

        row = result.fetchone()
        if row:
            round_value, gr_value, id_value, trx_value = row[0:4]
            crypto_value, fiat_value, buy_value, sell_value = row[4:8]
            pos_value, t_gain_value, r_gain_value = row[8:11]
            t_tax_value, crypto_prev, fiat_prev = row[11:14]
            buy_prev, r_tax, r_gain_net = row[14:17]
            t_gain_net, r_gain_prev, r_tax_prev = row[17:20]
            tax_disclos, tax_discre, audit = row[20:23]
            penalty, r_gain_final, lang = row[23:26]

            asset_type = "Unknown" 
            if gr_value == '2' and lang == 0:
                asset_type = "Crypto"
            elif gr_value == '2' and lang == 1:
                asset_type = "Kripto"
            elif gr_value == '1' and lang == 0:
                asset_type = "Stock"
            elif gr_value == '1' and lang == 1:
                asset_type = "Saham"

            if trx_value < 5:
                if pos_value == "s" and lang == 0:
                    pos_value = "SELL"
                elif pos_value == "s" and lang == 1:
                    pos_value = "JUAL"
                elif pos_value == "b" and lang == 0:
                    pos_value = "BUY"
                elif pos_value == "b" and lang == 1:
                    pos_value = "BELI"
            else:
                pos_value = "STOP"

            updated_data = {
                "round": round_value, "gr": gr_value, "id": id_value,
                "trx": trx_value, "crypto": crypto_value, "fiat": fiat_value,
                "buy": buy_value, "sell": sell_value, "pos": pos_value,
                "t_gain": t_gain_value, "r_gain": r_gain_value,
                "t_tax": t_tax_value, "asset_type": asset_type,
                "fiat_prev": fiat_prev, "crypto_prev": crypto_prev,
                "buy_prev": buy_prev, "r_tax": r_tax,
                "r_gain_net": r_gain_net, "t_gain_net": t_gain_net,
                "r_gain_prev": r_gain_prev, "r_tax_prev": r_tax_prev,
                "tax_disclos": tax_disclos, "tax_discre": tax_discre,
                "audit": audit, "penalty": penalty,
                "r_gain_final": r_gain_final, "lang": lang
            }
            return jsonify(updated_data)

# Main route for page navigation
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'language' in request.form:  # Initial form submission from index.html
            treatment_dict = insert_group_lang('Indonesian')
            id = treatment_dict["id"]
            treatment = treatment_dict["treatment"]
            lang = treatment_dict["lang"]
            au = treatment_dict["au"]
            return render_template('home-a.html', id=id, treatment=treatment, lang=lang, au=au)

        elif 'form_type' in request.form:
            form_type = request.form['form_type']
            id = request.form.get('id')
            treatment = request.form.get('treatment')
            lang = request.form.get('lang')
            au = request.form.get('au')

            if form_type == 'home':  # From home-a.html
                return render_template('form_demog-a.html', id=id, treatment=treatment, lang=lang, au=au)

            elif form_type == 'demographic':  # From form_demog-a.html
                gender = request.form.get('gender')
                age = request.form.get('age')
                education_level = request.form.get('education_level')
                current_education = request.form.get('current_education')
                country_residence = request.form.get('country_residence', 'indonesia')
                citizenship = request.form.get('citizenship', 'indonesia')
                asset_experience = ','.join(request.form.getlist('asset_experience[]'))
                tax_experience = request.form.get('tax_experience')
                description = request.form.get('description')

                insert_demog(gender, age, education_level, current_education, country_residence, 
                           citizenship, asset_experience, tax_experience, description, id)

                if treatment == "1":  # stock
                    return render_template('instruction-1-a.html', id=id, asset_type='stock', lang=lang, au=au)
                elif treatment == "2":  # crypto
                    return render_template('instruction-2-a.html', id=id, asset_type='crypto', lang=lang, au=au)

            elif form_type == 'instruction':  
                asset_type = request.form.get('asset_type')
                if asset_type == "stock":
                    gr = "1"
                elif asset_type == "crypto":
                    gr = "2"
                else:
                    gr = "unknown"
                insert_group_treatment(gr, id, lang)
                if asset_type == "stock" and lang=="0":
                    return render_template('instruction-tryout-1.html', id=id, asset_type=asset_type, lang=lang)
                elif asset_type == "stock" and lang=="1":
                    return render_template('instruction-tryout-1-a.html', id=id, asset_type=asset_type, lang=lang)
                elif asset_type == "crypto" and lang=="0":
                    return render_template('instruction-tryout-2.html', id=id, asset_type=asset_type, lang=lang)
                elif asset_type == "crypto" and lang=="1":
                    return render_template('instruction-tryout-2-a.html', id=id, asset_type=asset_type, lang=lang)

            elif form_type == 'start':
                id = request.form.get('id')
                lang = request.form.get('lang')
                if id:
                    init_data = fetch_init_data(id)
                    if init_data and lang == "0":
                        return render_template('round0.html', data=init_data)
                    elif init_data and lang == "1":
                        return render_template('round0-a.html', data=init_data)
                return "Error: Invalid ID"

            elif form_type == 'tryout':
                with engine.connect() as conn:
                    select_statement = text("""
                        SELECT round, gr 
                        FROM `teg-simulation-sandbox`.responses
                        WHERE id = :user_id
                        ORDER BY ts DESC
                        LIMIT 1
                    """)
                    result = conn.execute(select_statement, {"user_id": id})
                    latest_round, gr = result.fetchone()

                    if latest_round < 15:
                        next_round = latest_round + 1
                        conn.execute(
                            text("INSERT INTO `teg-simulation-sandbox`.responses(round,gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, tax_disclos, audit, t_gain_net, r_gain_net,r_tax,sec,price,crypto_prev, fiat_prev, buy_prev, r_gain_prev,r_tax_prev, lang)VALUES (:round, :gr, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',:lang)"),
                            {"round": next_round, "gr": gr, "id": id, "lang": lang}
                        )
                        init_data = fetch_init_data(id)
                        if init_data:
                            if lang == '0':
                                return render_template('rounds.html', data=init_data)
                            elif lang == '1':
                                return render_template('rounds-a.html', data=init_data)
            elif form_type == 'tax_reporting':
                response = retrieve_data(id)
                response_data = response.json
                template_name = 'tax_reporting-a.html' if response_data['lang'] == 1 else 'tax_reporting.html'
                if 'lang' in response_data and response_data['lang'] in [0, 1]:
                    return render_template(template_name, summary_data=response_data)
                else:
                    return "Error: Invalid ID"

            elif form_type == 'tax_disclosure':
                taxdisclos = request.form.get('tax_disclos', '').replace(',', '')
                audit_value = 0 if random.random() < 0.8 else 1

                if not id or not lang or taxdisclos is None:
                    return "Missing data", 400

                with engine.begin() as conn:
                    update_statement = text("""
                        UPDATE `teg-simulation-sandbox`.`responses`
                        SET `tax_disclos` = :new_tax_disclos_value, `audit` = :audit_value
                        WHERE `id` = :user_id
                        ORDER BY `ts` DESC
                        LIMIT 1
                    """)
                    conn.execute(update_statement, {
                        "new_tax_disclos_value": taxdisclos, 
                        "audit_value": audit_value, 
                        "user_id": id
                    })

                    select_statement = text("""
                        SELECT `round`, `audit`
                        FROM `teg-simulation-sandbox`.`responses`
                        WHERE `id` = :user_id
                        ORDER BY `ts` DESC
                        LIMIT 1
                    """)
                    result = conn.execute(select_statement, {"user_id": id})
                    latest_round, latest_audit = result.fetchone()

                template_name = f"tax_audit_{'1' if latest_audit == 1 else '0'}{'-a' if lang == '1' else ''}.html"
                response_data = retrieve_data(id).json
                return render_template(template_name, summary_data=response_data)

            elif form_type == 'next_round':
                with engine.connect() as conn:
                    select_statement = text("""
                        SELECT `round`, `gr` 
                        FROM `teg-simulation-sandbox`.`responses`
                        WHERE `id` = :user_id
                        ORDER BY `ts` DESC
                        LIMIT 1
                    """)
                    result = conn.execute(select_statement, {"user_id": id})
                    latest_round, gr = result.fetchone()

                    if latest_round < 15:
                        next_round = latest_round + 1
                        conn.execute(
                            text("INSERT INTO `teg-simulation-sandbox`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`, `r_gain`, `t_tax`, `tax_disclos`, `audit`, `t_gain_net`, `r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`, `buy_prev`, `r_gain_prev`,`r_tax_prev`, `lang`)VALUES (:round, :gr, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',:lang)"),
                            {"round": next_round, "gr": gr, "id": id, "lang": lang}
                        )
                        init_data = fetch_init_data(id)
                        if init_data:
                            if lang == '0':
                                return render_template('rounds.html', data=init_data)
                            elif lang == '1':
                                return render_template('rounds-a.html', data=init_data)
                    else:
                        random_number = random.randint(1, 15)
                        select_statement_2 = text("""
                            SELECT `id`, `gr`,`round`, `r_gain_final`, `lang`
                            FROM `teg-simulation-sandbox`.`responses`
                            WHERE `id` = :user_id AND `round` = :random_number
                            ORDER BY `ts` DESC
                            LIMIT 1
                        """)
                        result_2 = conn.execute(select_statement_2, {
                            "user_id": id, 
                            "random_number": random_number
                        })
                        result = result_2.fetchone()

                        if result is None:
                            print("No data found in select_statement_2")
                            return "No data found"

                        user_id, gr, comp_round, comp_amt, lang = result

                        if lang == 0:
                            if comp_amt < 1000000:
                                comp_rgainfinal = 5
                            elif 1000000 <= comp_amt <= 5000000:
                                comp_rgainfinal = 10
                            else:
                                comp_rgainfinal = 20
                        elif lang == 1:
                            if comp_amt < 1000000:
                                comp_rgainfinal = 50000
                            elif 1000000 <= comp_amt <= 5000000:
                                comp_rgainfinal = 100000
                            else:
                                comp_rgainfinal = 200000

                        if lang == 0:
                            return render_template("the_random_picker.html", user_id=user_id, comp_round=comp_round, comp_amt=comp_amt, comp_rgainfinal=comp_rgainfinal, gr=gr, lang=lang)
                        elif lang == 1:
                            return render_template("the_random_picker-a.html", user_id=user_id, comp_round=comp_round, comp_amt=comp_amt, comp_rgainfinal=comp_rgainfinal, gr=gr, lang=lang)

            elif form_type == 'survey':

                # Get all necessary variables from form data
                id = request.form.get('id')
                gr = request.form.get('gr')
                lang = request.form.get('lang')
                comp_amt = request.form.get('comp_amt')
                comp_round = request.form.get('comp_round')
                comp_rgainfinal = request.form.get('comp_rgainfinal')

                # Validate required data
                if not all([id, gr, lang]):
                    return "Missing required data", 400

                # If compensation data exists, insert it into the compensation table
                if comp_amt and comp_round and comp_rgainfinal:
                    gr = str(gr).replace('\n', '').strip()[:1]  # Clean up gr value as in legacy code
                    with engine.connect() as conn:
                        insert_statement = text("""
                            INSERT INTO compensation (comp_amt, id, comp_round, comp_rgainfinal, gr, lang)
                            VALUES (:comp_amt, :id, :comp_round, :comp_rgainfinal, :gr, :lang)
                        """)
                        conn.execute(
                            insert_statement,
                            {
                                "comp_amt": comp_amt, 
                                "id": id, 
                                "comp_round": comp_round, 
                                "comp_rgainfinal": comp_rgainfinal, 
                                "gr": gr, 
                                "lang": lang
                            }
                        )

                        # Optional: Print debug information
                        print(f"Recorded compensation - UserID: {id}, Group: {gr}, CompAmt: {comp_amt}, CompRound: {comp_round}, CompRoundGain: {comp_rgainfinal}, Lang: {lang}")

                    
                    questions = [
                    ' ... because to me it’s obvious that this is what you do.',
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
                    'How likley will you pay your crypto taxes for the current year correctly and in full extent to the tax authority?'
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

                    if lang == '0':
                         return render_template('the_survey.html', id=id, gr=gr, lang=lang, questions=questions)
                    elif lang == '1':
                        return render_template('the_survey-a.html', id=id, gr=gr, lang=lang, questions=questindo)
                    else:
                        return "Error: Invalid language selection"

            elif form_type == 'survey_end':
                form_data = dict(request.form)
                email = form_data.get('email')
                gr = form_data.get('gr')
                id = form_data.get('id')
                comments = form_data.get('comments')
                followup = form_data.get('followup')
                lang = form_data.get('lang')
                veteran = form_data.get('veteran')
                cryptorisk = form_data.get('cryptorisk')
                trustpower = form_data.get('trustpower')
                comments_a = form_data.get('comments_a')
                comments_b = form_data.get('comments_b')

                question_columns = {f'question{i}': f'question{i}' for i in range(37)}
                insert_values = {}

                for question_num, answer in form_data.items():
                    if question_num in question_columns:
                        column_name = question_columns[question_num]
                        insert_values[column_name] = answer

                insert_values.update({
                    'email': email, 'gr': gr, 'id': id,
                    'comments': comments, 'followup': followup,
                    'lang': lang, 'veteran': veteran,
                    'cryptorisk': cryptorisk, 'trustpower': trustpower,
                    'comments_a': comments_a, 'comments_b': comments_b
                })

                with engine.connect() as conn:
                    insert_statement = text("""
                        INSERT INTO survey (
                            question0, question1, question2, question3, question4, question5, 
                            question6, question7, question8, question9, question10, question11,
                            question12, question13, question14, question15, question16, question17,
                            question18, question19, question20, question21, question22, question23,
                            question24, question25, question26, question27, question28, question29,
                            question30, question31, question32, question33, question34, question35,
                            question36, email, gr, id, comments, followup, lang, veteran, 
                            cryptorisk, trustpower, comments_a, comments_b
                        ) VALUES (
                            :question0, :question1, :question2, :question3, :question4, :question5,
                            :question6, :question7, :question8, :question9, :question10, :question11,
                            :question12, :question13, :question14, :question15, :question16, :question17,
                            :question18, :question19, :question20, :question21, :question22, :question23,
                            :question24, :question25, :question26, :question27, :question28, :question29,
                            :question30, :question31, :question32, :question33, :question34, :question35,
                            :question36, :email, :gr, :id, :comments, :followup, :lang, :veteran,
                            :cryptorisk, :trustpower, :comments_a, :comments_b
                        )
                    """)
                    conn.execute(insert_statement, insert_values)

                if lang == '1':
                    return render_template('the_survey_ends-a.html')
                else:
                    return render_template('the_survey_ends.html')

    # For GET requests, show index page
    return render_template('index.html')

# Jinja filter for crypto formatting
def format_crypto(value, lang):
    if isinstance(value, Decimal):
        if lang == 1:  # Indonesian
            return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
        else:  # Default to English
            return "{:,.2f}".format(value)
    return value

app.jinja_env.filters['format_crypto'] = format_crypto


@app.route('/survey-test', methods=['GET'])
def survey_test():
    # Test values
    id = "test123"
    gr = "2"  # or "1" depending on what you want to test
    lang = "1"  # "1" for Indonesian version

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

    return render_template('the_survey-a.html', id=id, gr=gr, lang=lang, questions=questindo)

# Run the application
if __name__ == "__main__":
    import sys
    from os import environ
    try:
        port = int(environ.get("PORT", 3000))
        app.run(
            host="0.0.0.0",
            port=port,
            debug=True,
            use_reloader=True
        )
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)


