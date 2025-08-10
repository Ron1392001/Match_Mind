from flask import Flask, render_template, request, redirect, url_for
import re 



app = Flask(__name__)

# נתוני שחקנים לפי מחזור
players_by_round = {}

def get_top_3_players(players):
    return sorted(players, key=lambda x: x['goals'], reverse=True)[:3]

@app.route('/')
def login_page():
    if not players_by_round:
        return render_template('loginpage.html', last_round=None, top_players=[])
    
    last_round = sorted(players_by_round.keys(), reverse=True)[0]
    players = players_by_round.get(last_round, [])
    top_players = get_top_3_players(players)
    return render_template('loginpage.html', last_round=last_round, top_players=top_players)

@app.route('/data', methods=['GET', 'POST'])
def data_page():
    selected_round = request.form.get('round')
    search_name = request.form.get('search_name', '').lower()
    search_team = request.form.get('search_team', '').lower()

    filtered_data = []
    rounds = sorted(players_by_round.keys(), reverse=True)

    if selected_round:
        for player in players_by_round.get(selected_round, []):
            if (search_name and search_name not in player['name'].lower()) or \
               (search_team and search_team not in player['team_name'].lower()):
                continue
            filtered_data.append(player)

    return render_template('data.html', rounds=rounds, filtered_data=filtered_data)

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    message = ""
    if request.method == 'POST':
        round_ = request.form['round']
        player = {
            'name': request.form['player_name'],
            'team_name': request.form['team_name'],
            'goals': int(request.form['goals']),
            'assists': int(request.form['assists']),
            'key_passes': int(request.form['key_passes']),
            'accurate_passes': int(request.form['accurate_passes']),
            'chances_created': int(request.form['chances_created']),
            'sprints': int(request.form['sprints']),
            'xg': float(request.form['xg']),
            'dribble_success': float(request.form['dribble_success']),
            'tackle_success': float(request.form['tackle_success']),
            'aerial_duels_success': float(request.form['aerial_duels_success'])
        }

        if round_ not in players_by_round:
            players_by_round[round_] = []
        players_by_round[round_].append(player)
        message = "🟢 שחקן נוסף בהצלחה!"

    return render_template('admin.html', message=message, matches_data=players_by_round)

@app.route('/admin/delete', methods=['POST'])
def delete_player():
    round_ = request.form.get('round')
    player_name = request.form.get('player_name')

    if round_ in players_by_round:
        players_by_round[round_] = [p for p in players_by_round[round_] if p['name'] != player_name]

    return redirect(url_for('admin_page'))

@app.route('/admin/edit', methods=['GET', 'POST'])
def edit_player():
    if request.method == 'GET':
        round_ = request.args.get('round')
        player_name = request.args.get('player_name')

        player = next((p for p in players_by_round.get(round_, []) if p['name'] == player_name), None)
        return render_template('edit_player.html', round_name=round_, player=player)

    elif request.method == 'POST':
        round_ = request.form['round']
        original_name = request.form['original_name']

        updated_player = {
            'name': request.form['player_name'],
            'team_name': request.form['team_name'],
            'goals': int(request.form['goals']),
            'assists': int(request.form['assists']),
            'key_passes': int(request.form['key_passes']),
            'accurate_passes': int(request.form['accurate_passes']),
            'chances_created': int(request.form['chances_created']),
            'sprints': int(request.form['sprints']),
            'xg': float(request.form['xg']),
            'dribble_success': float(request.form['dribble_success']),
            'tackle_success': float(request.form['tackle_success']),
            'aerial_duels_success': float(request.form['aerial_duels_success']),
        }

        # החלפת שחקן
        if round_ in players_by_round:
            players_by_round[round_] = [
                updated_player if p['name'] == original_name else p
                for p in players_by_round[round_]
            ]

        return redirect(url_for('admin_page'))

def summarize_player_data(player_rounds):
    return {
        'name': player_rounds[0]['name'],
        'team_name': player_rounds[0]['team_name'],
        'total_goals': sum(p['goals'] for p in player_rounds),
        'total_assists': sum(p['assists'] for p in player_rounds),
        'avg_xg': round(sum(p['xg'] for p in player_rounds) / len(player_rounds), 2),
        'avg_key_passes': round(sum(p['key_passes'] for p in player_rounds) / len(player_rounds), 2),
        'avg_dribble_success': round(sum(p['dribble_success'] for p in player_rounds) / len(player_rounds), 1),
        'avg_tackle_success': round(sum(p['tackle_success'] for p in player_rounds) / len(player_rounds), 1),
        'avg_aerial_duels_success': round(sum(p['aerial_duels_success'] for p in player_rounds) / len(player_rounds), 1),
        'total_chances_created': sum(p.get('chances_created', 0) for p in player_rounds),
        'total_sprints': sum(p.get('sprints', 0) for p in player_rounds),
    }



@app.route('/compare', methods=['GET', 'POST'])
def compare_players():
    # רשימת כל השחקנים להצעה בטופס
    all_player_names = []
    seen = set()
    for round_players in players_by_round.values():
        for player in round_players:
            if player['name'] not in seen:
                all_player_names.append(player['name'])
                seen.add(player['name'])

    if request.method == 'POST':
        selected_names = [request.form.get('player1'), request.form.get('player2')]
        summarized_players = []

        for name in selected_names:
            player_rounds = []
            for round_players in players_by_round.values():
                for p in round_players:
                    if p['name'] == name:
                        player_rounds.append(p)

            if player_rounds:
                summary = summarize_player_data(player_rounds)
                summarized_players.append(summary)

        fields = [
            'total_goals',
            'total_assists',
            'avg_xg',
            'avg_key_passes',
            'total_chances_created',
            'total_sprints',
            'avg_dribble_success',
            'avg_tackle_success',
            'avg_aerial_duels_success'
        ]
        

        # קביעת צבעים לפי הערכים הטובים והגרועים
        best = {f: max(p[f] for p in summarized_players) for f in fields}
        worst = {f: min(p[f] for p in summarized_players) for f in fields}

        for p in summarized_players:
            colors = {}
            for f in fields:
                if p[f] == best[f]:
                    colors[f] = 'green'
                elif p[f] == worst[f]:
                    colors[f] = 'red'
                else:
                    colors[f] = 'neutral'
            p['colors'] = colors

        return render_template('compare.html', comparison_data=summarized_players, fields=fields, player_names=all_player_names)

    # GET request - מציג טופס ריק
    return render_template('compare.html', comparison_data=None, fields=None, player_names=all_player_names)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_player():
    player_data = []
    summary = {}
    peaks = {}

    def round_key(x):
        # מנסה לשלוף מספר מתוך מחרוזת מחזור (למשל "מחזור 1")
        match = re.search(r'\d+', x['round'])
        return int(match.group()) if match else 0

    if request.method == 'POST':
        name = request.form.get('player_name', '').strip().lower()
        print(f"חיפוש שחקן בשם: '{name}'")

        player_data = []
        for round_, players in players_by_round.items():
            for p in players:
                print(f"בודק שחקן: '{p['name']}'")
                # חיפוש חלקי (תואם גם אם המשתמש כתב רק חלק מהשם)
                if name in p['name'].lower():
                    player_with_round = p.copy()
                    player_with_round['round'] = round_
                    player_data.append(player_with_round)

        print(f"נמצאו {len(player_data)} תוצאות")

        if player_data:
            player_data.sort(key=round_key)

            summary = {
                'total_goals': sum(p['goals'] for p in player_data),
                'total_assists': sum(p['assists'] for p in player_data),
                'avg_xg': round(sum(p['xg'] for p in player_data) / len(player_data), 2),
                'avg_key_passes': round(sum(p['key_passes'] for p in player_data) / len(player_data), 2),
                'avg_dribble_success': round(sum(p['dribble_success'] for p in player_data) / len(player_data), 1),
            }

            peaks = {
                'max_goals': max(player_data, key=lambda x: x['goals']),
                'max_assists': max(player_data, key=lambda x: x['assists']),
                'max_xg': max(player_data, key=lambda x: x['xg']),
            }

    return render_template(
        'analyze.html',
        player_data=player_data,
        summary=summary,
        peaks=peaks
    )


if __name__ == '__main__':
    app.run(debug=True)
