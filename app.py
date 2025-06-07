from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

player_score = 0
cpu_score = 0
current_round = 0
wallet = 1000.00
current_bet = 0.00

EMPEROR_MULTIPLIER = 0.5
SLAVE_MULTIPLIER = 2.0

hands = {
    'player': [],
    'cpu': []
}


def generate_hands(round_number):
    slave_hand = ['S'] + ['C'] * 4
    king_hand = ['K'] + ['C'] * 4
    return (slave_hand, king_hand) if round_number % 2 == 0 else (king_hand, slave_hand)


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


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start', methods=['POST'])
def start_game():
    global hands, current_round, current_bet

    if current_round == 0:
        current_bet = 100.00
    else:
        data = request.get_json()
        if data is None or 'bet' not in data:
            return jsonify({'error': 'Bet amount is required.'}), 400
        try:
            bet = round(float(data['bet']), 2)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid bet value.'}), 400
        if bet > wallet:
            return jsonify({'error': 'Insufficient funds for this bet.'}), 400
        current_bet = bet

    p1_hand, cpu_hand = generate_hands(current_round)
    hands['player'] = p1_hand
    hands['cpu'] = cpu_hand
    current_round += 1

    return jsonify({
        'p1_hand': p1_hand,
        'player_score': player_score,
        'cpu_score': cpu_score,
        'wallet': round(wallet, 2)
    })


@app.route('/play', methods=['POST'])
def play_turn():
    global player_score, cpu_score, hands, wallet, current_bet

    data = request.get_json()
    selected_card = data.get('card')

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
            # Correct wallet update when player wins:
            if selected_card == 'K':
                wallet += round(current_bet * EMPEROR_MULTIPLIER, 2)
            elif selected_card == 'S':
                wallet += round(current_bet * SLAVE_MULTIPLIER, 2)
            elif selected_card == 'C':
                wallet += round(current_bet * EMPEROR_MULTIPLIER, 2)
        elif winner == 'cpu':
            wallet -= round(current_bet, 2)
            cpu_score += 1

        new_p1_hand, new_cpu_hand = generate_hands(current_round)
        hands['player'] = new_p1_hand
        hands['cpu'] = new_cpu_hand

    return jsonify({
        'p1_card': selected_card,
        'cpu_card': cpu_card,
        'winner': winner,
        'player_score': player_score,
        'cpu_score': cpu_score,
        'wallet': round(wallet, 2),
        'remaining_player_hand': hands['player'],
        'reset': round_ended,
    })

@app.route('/reset', methods=['POST'])
def reset_game():
    global player_score, cpu_score, current_round, wallet, current_bet, hands

    player_score = 0
    cpu_score = 0
    current_round = 0
    wallet = 1000.00
    current_bet = 0.00
    hands = {'player': [], 'cpu': []}

    return jsonify({'wallet': round(wallet, 2)})


if __name__ == '__main__':
    app.run(debug=True)
