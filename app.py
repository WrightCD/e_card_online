from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

#Game Scores will make more dynamic with betting later on
player_score = 0
cpu_score = 0
current_round = 0

def generate_hands(round_number):
    slave_hand = ['S'] + ['C']*4
    king_hand = ['K'] + ['C'] * 4

    if round_number % 2 == 0:
        p1_hand = slave_hand
        cpu_hand = king_hand
    else:
        p1_hand = king_hand
        cpu_hand = slave_hand

    return p1_hand, cpu_hand

def determine_winner(p1_card, cpu_card):
    rules = {
        ('S', 'K'): 'player',
        ('S', 'C'): 'cpu',
        ('C', 'K'): 'cpu',
        ('C', 'C'): 'draw',
        ('C', 'S'): 'player',
        ('K', 'C'): 'player',
        ('K', 'S'): 'cpu',
    }
    return rules.get((p1_card, cpu_card), 'draw')

hands = {
    'player': [],
    'cpu': []
}

@app.route('/')
def index():  # put application's code here
    return render_template("index.html")

@app.route('/start', methods=['POST'])
def start_game():
    global hands, current_round, player_score, cpu_score
    p1_hand, cpu_hand = generate_hands(current_round)
    current_round += 1
    hands['player'] = p1_hand
    hands['cpu'] = cpu_hand
    return jsonify({
        'p1_hand': p1_hand,
        'player_score': player_score,
        'cpu_score': cpu_score
    })


@app.route('/play', methods=['POST'])
def play_turn():
    global player_score, cpu_score, hands

    data = request.get_json()
    selected_card = data['card']

    if selected_card not in hands['player']:
        return jsonify({'error': 'Invalid card'}), 400

    hands['player'].remove(selected_card)

    cpu_card = random.choice(hands['cpu'])
    hands['cpu'].remove(cpu_card)

    winner = determine_winner(selected_card, cpu_card)

    round_ended = selected_card in ['S', 'K'] or cpu_card in ['S', 'K']

    if round_ended:
        if winner == 'player':
            player_score += 1
        elif winner == 'cpu':
            cpu_score += 1

        # Reset hands for new round
        new_p1_hand, new_cpu_hand = generate_hands(current_round)
        hands['player'] = new_p1_hand
        hands['cpu'] = new_cpu_hand
        reset = True
    else:
        reset = False

    return jsonify({
        'p1_card': selected_card,
        'cpu_card': cpu_card,
        'winner': winner,
        'player_score': player_score,
        'cpu_score': cpu_score,
        'remaining_player_hand': hands['player'],
        'reset': reset
    })


if __name__ == '__main__':
    app.run(debug=True)
