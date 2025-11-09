"""
Selecciona opción 1
Habla al micrófono por 3 segundos
El sistema analiza y muestra resultados automáticamente

Salida esperada:
============================================================
ESTADO EMOCIONAL: ANSIEDAD
 NIVEL DE RIESGO: MEDIO
============================================================
confianza = 78
caracteristicas = "Volumen elevado | Habla acelerada | Energía vocal irregular"

# Métricas:
#    Volumen: 0.142
Tono: 267.3 Hz
Tempo: 185.2 BPM
Pausas: 0.8 s
Ratio de habla: 87%
============================================================
"""

EXPECTED_OUTPUT = """============================================================
ESTADO EMOCIONAL: ANSIEDAD
 NIVEL DE RIESGO: MEDIO
============================================================
confianza = 78
caracteristicas = "Volumen elevado | Habla acelerada | Energía vocal irregular"

# Ejemplo de impresión de resultados:
print(f"Confianza: {confianza}%")
print(caracteristicas)
print('''
Métricas:
   Volumen: 0.142
   Tono: 267.3 Hz
   Tempo: 185.2 BPM
   Pausas: 0.8 s
   Ratio de habla: 87%
============================================================
''')

def print_expected_output():
    print(EXPECTED_OUTPUT)

if __name__ == "__main__":
    print_expected_output()

# End of file


# End of file

estado_emocional = "ANSIEDAD"
nivel_riesgo = "MEDIO"

# Confianza: 78%
# Volumen elevado | Habla acelerada | Energía vocal irregular


# Métricas
volumen = 0.142

def get_frequency_hz():
    return "267.3 Hz"

tono = get_frequency_hz()
tempo = 185.2  # BPM
pausas = 0.8   # s
ratio_habla = 87  # %

# ============================================================
"""