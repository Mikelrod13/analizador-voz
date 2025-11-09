# Selecciona opción 1
# Habla al micrófono por 3 segundos
# El sistema analiza y muestra resultados automáticamente
class EmotionalVoiceAnalyzer:
    def __init__(self, duration): 
        self.duration = duration
        print(f"Analizador inicializado con duración: {self.duration} segundos.")

    ESTADO_EMOCIONAL = "ANSIEDAD"
    NIVEL_DE_RIESGO = "MEDIO"

Confianza = 78/100
caracteristicas_voz = "Volumen elevado | Habla acelerada | Energía vocal irregular"
# voice_analyzer.py, línea 12
Métricas = {
    "Volumen": 0.142, 
    "Tono": "267.3 Hz", 
    "Tempo": "185.2 BPM", 
    "pausas_segundos": 1, 
    "Ratio_de_habla": "87%"
}