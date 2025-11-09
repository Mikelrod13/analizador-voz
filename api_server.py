from flask import Flask, jsonify, request
from flask_cors import CORS
from voice_analyzer import EmotionalVoiceAnalyzer
import threading
import time

app = Flask(__name__)
CORS(app)

analyzer = EmotionalVoiceAnalyzer(duration=3)
current_state = {'emotion': 'neutral', 'risk': 'normal'}
is_analyzing = False

def continuous_analysis():
    """Análisis continuo en background."""
    global current_state, is_analyzing
    while is_analyzing:
        audio = analyzer.record_audio_segment()
        features = analyzer.extract_features(audio)
        if features:
            emotion, risk, conf, expl = analyzer.classify_emotion(features)
            current_state = {
                'emotion': emotion,
                'risk_level': risk,
                'confidence': conf,
                'explanation': expl,
                'timestamp': time.time()
            }
        time.sleep(1)

@app.route('/api/start', methods=['POST'])
def start_analysis():
    """Inicia el análisis de voz."""
    global is_analyzing
    if not is_analyzing:
        is_analyzing = True
        thread = threading.Thread(target=continuous_analysis)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/api/stop', methods=['POST'])
def stop_analysis():
    """Detiene el análisis."""
    global is_analyzing
    is_analyzing = False
    return jsonify({'status': 'stopped'})

@app.route('/api/state', methods=['GET'])
def get_state():
    """Obtiene el estado emocional actual."""
    return jsonify(current_state)

@app.route('/api/emergency', methods=['POST'])
def emergency():
    """Activa protocolo de emergencia."""
    # Aquí conectar con Twilio, enviar SMS, etc.
    return jsonify({
        'status': 'emergency_activated',
        'action': 'calling_crisis_line',
        'number': '800-911-2000'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)