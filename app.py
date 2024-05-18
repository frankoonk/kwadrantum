from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import datetime
import ephem
import random
import math

app = Flask(__name__)

# Helper function to calculate numerology number
def numerology_number(date):
    total = sum(int(char) for char in date.strftime('%Y%m%d'))
    while total > 9:
        total = sum(int(char) for char in str(total))
    return total

# Helper function to get real-time planetary positions with added volatility
def get_volatile_planetary_positions(date, seconds, param1, param2, param3, param4):
    planets = [ephem.Sun(), ephem.Moon(), ephem.Mars(), ephem.Venus(), ephem.Jupiter()]
    positions = {planet.name: [] for planet in planets}

    for second in range(seconds):
        current_time = date + datetime.timedelta(seconds=second)
        for planet in planets:
            planet.compute(current_time)
            base_value = planet.ra + planet.dec
            volatile_value = base_value + param1 * math.sin(second / 10) + param2 * math.cos(second / 15) + param3 * math.sin(second / 20) + param4 * math.cos(second / 25) + random.uniform(-10, 10)
            positions[planet.name].append((second, volatile_value))

    return positions

# Helper function to calculate intensity, love, relationship, and synergy
def calculate_values(name1, birthdate1, name2, birthdate2, name3, birthdate3, param1, param2, param3, param4):
    def name_value(name):
        return sum(ord(char) for char in name) % 100

    def generate_weights():
        return [random.uniform(0.8, 1.2) for _ in range(3)]

    num1 = numerology_number(birthdate1)
    num2 = numerology_number(birthdate2)
    num3 = numerology_number(birthdate3)

    weight_intensity = generate_weights()
    weight_love = generate_weights()
    weight_relationship = generate_weights()
    weight_synergy = generate_weights()

    value1 = (name_value(name1) + num1 + param1 + param2 + param3 + param4) % 100
    value2 = (name_value(name2) + num2 + param1 + param2 + param3 + param4) % 100
    value3 = (name_value(name3) + num3 + param1 + param2 + param3 + param4) % 100

    intensity = (value1 * weight_intensity[0] + value2 * weight_intensity[1] + value3 * weight_intensity[2]) / 3
    love = (value1 * weight_love[0] * value2 * weight_love[1] * value3 * weight_love[2]) % 100
    relationship = (math.sin(value1) * weight_relationship[0] + math.cos(value2) * weight_relationship[1] + math.tan(value3) * weight_relationship[2]) % 100
    synergy = (value1 * weight_synergy[0] + value2 * weight_synergy[1] + value3 * weight_synergy[2]) / 3

    contributions = {
        'intensity': [value1 * weight_intensity[0], value2 * weight_intensity[1], value3 * weight_intensity[2]],
        'love': [value1 * weight_love[0], value2 * weight_love[1], value3 * weight_love[2]],
        'relationship': [math.sin(value1) * weight_relationship[0], math.cos(value2) * weight_relationship[1], math.tan(value3) * weight_relationship[2]],
        'synergy': [value1 * weight_synergy[0], value2 * weight_synergy[1], value3 * weight_synergy[2]]
    }

    return intensity, love, relationship, synergy, contributions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_graph', methods=['POST'])
def update_graph():
    data = request.json
    birthdate1 = datetime.datetime.strptime(data['birthdate1'], '%Y-%m-%d').date()
    birthdate2 = datetime.datetime.strptime(data['birthdate2'], '%Y-%m-%d').date()
    birthdate3 = datetime.datetime.strptime(data['birthdate3'], '%Y-%m-%d').date()

    intensity, love, relationship, synergy, contributions = calculate_values(
        data['name1'], birthdate1,
        data['name2'], birthdate2,
        data['name3'], birthdate3,
        int(data['parameter1']), int(data['parameter2']), int(data['parameter3']), int(data['parameter4'])
    )

    planetary_positions = get_volatile_planetary_positions(datetime.datetime.utcnow(), 60, int(data['parameter1']), int(data['parameter2']), int(data['parameter3']), int(data['parameter4']))

    fig = go.Figure()

    # Plot volatile planetary positions
    for planet, pos_data in planetary_positions.items():
        times, values = zip(*pos_data)
        fig.add_trace(go.Scatter(x=times, y=values, mode='lines', name=f'{planet} Position'))

    fig.update_layout(
        title='Volatile Planetary Positions',
        xaxis_title='Seconds since calculation',
        yaxis_title='Volatile Value'
    )

    graphJSON = fig.to_json()
    response = {
        'graphJSON': graphJSON,
        'intensity': intensity,
        'love': love,
        'relationship': relationship,
        'synergy': synergy,
        'contributions': contributions
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
