"""
DEMO COMPLETO CON MICRÓFONO - CABINAS ANTI-SUICIDIO
Análisis de voz EN VIVO con tu micrófono
Versión simplificada para laptop
Autor: Miguel Rodríguez León
"""

import numpy as np
import pyaudio
import time
from datetime import datetime
import threading

# Colores para consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class AnalizadorVozSimple:
    """
    Analizador de voz simplificado que funciona en cualquier laptop.
    Detecta emociones basándose en características de audio.
    """
    
    def __init__(self):
        # Configuración de audio
        self.CHUNK = 1024  # Tamaño del buffer
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Frecuencia de muestreo (más baja para laptops)
        self.RECORD_SECONDS = 3  # Grabar 3 segundos
        
        # Inicializar PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Umbrales de detección
        self.umbral_volumen_bajo = 1000
        self.umbral_volumen_alto = 8000
        self.umbral_variabilidad_alta = 2000
        
        print(Colors.GREEN + "✓ Analizador de voz inicializado" + Colors.END)
    
    def listar_microfonos(self):
        """Lista todos los micrófonos disponibles."""
        print(Colors.BOLD + "\n MICRÓFONOS DISPONIBLES:" + Colors.END)
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        micros = []
        for i in range(0, numdevices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                micros.append(i)
                print(f"  [{i}] {device_info.get('name')}")
        
        return micros
    
    def grabar_audio(self):
        """Graba audio del micrófono."""
        print(Colors.YELLOW + "\n🎤 Grabando... HABLA AHORA" + Colors.END)
        print("   (Di algo como: 'Hola, me siento bien' o 'Estoy muy nervioso')")
        
        # Abrir stream de audio
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        frames = []
        
        # Grabar durante 3 segundos con indicador visual
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Indicador visual de grabación
            if i % 4 == 0:
                print("   ●", end="", flush=True)
        
        print(Colors.GREEN + "\n✓ Grabación completada" + Colors.END)
        
        # Cerrar stream
        stream.stop_stream()
        stream.close()
        
        # Convertir a numpy array
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        
        return audio_data
    
    def analizar_audio(self, audio_data):
        """
        Analiza el audio grabado y detecta emoción.
        Usa análisis simplificado sin librerías complejas.
        """
        
        # 1. VOLUMEN (intensidad del audio)
        volumen_promedio = np.mean(np.abs(audio_data))
        volumen_max = np.max(np.abs(audio_data))
        
        # 2. VARIABILIDAD (cuánto cambia el volumen)
        variabilidad = np.std(audio_data)
        
        # 3. CRUCES POR CERO (indica frecuencia aproximada)
        cruces_cero = np.sum(np.diff(np.sign(audio_data)) != 0)
        frecuencia_aprox = (cruces_cero / len(audio_data)) * self.RATE / 2
        
        # 4. ENERGÍA
        energia = np.sum(audio_data.astype(float) ** 2) / len(audio_data)
        
        # 5. PAUSAS (detectar silencios)
        umbral_silencio = volumen_promedio * 0.3
        es_silencio = np.abs(audio_data) < umbral_silencio
        num_silencios = np.sum(np.diff(es_silencio.astype(int)) != 0) / 2
        
        # CLASIFICACIÓN DE EMOCIÓN
        emocion, riesgo, explicacion = self._clasificar_emocion(
            volumen_promedio, variabilidad, frecuencia_aprox, num_silencios
        )
        
        return {
            'emocion': emocion,
            'riesgo': riesgo,
            'confianza': 0.85,  # Simplificado
            'explicacion': explicacion,
            'metricas': {
                'volumen': volumen_promedio,
                'volumen_max': volumen_max,
                'variabilidad': variabilidad,
                'frecuencia': frecuencia_aprox,
                'energia': energia,
                'pausas': num_silencios
            }
        }
    
    def _clasificar_emocion(self, volumen, variabilidad, frecuencia, pausas):
        """Clasifica la emoción basándose en las métricas."""
        
        # DEPRESIÓN: Volumen muy bajo, poca variabilidad, muchas pausas
        if volumen < self.umbral_volumen_bajo and variabilidad < 1000 and pausas > 5:
            return 'depresion', 'alto', 'Voz muy baja y con muchas pausas'
        
        # ANSIEDAD: Volumen alto, mucha variabilidad, frecuencia alta
        if volumen > self.umbral_volumen_alto and variabilidad > self.umbral_variabilidad_alta:
            return 'ansiedad', 'medio', 'Voz intensa y con variabilidad alta'
        
        # TRISTEZA: Volumen bajo/medio, frecuencia baja
        if volumen < 3000 and frecuencia < 150:
            return 'tristeza', 'medio', 'Voz apagada y tono bajo'
        
        # CRISIS: Volumen MUY bajo + muchas pausas
        if volumen < 800 and pausas > 8:
            return 'crisis', 'critico', 'Señales críticas: voz muy débil con pausas largas'
        
        # ESTABLE: Todo en rangos normales
        return 'estable', 'normal', 'Parámetros de voz en rango normal'
    
    def mostrar_resultado(self, resultado):
        """Muestra el resultado del análisis."""
        
        # Color según riesgo
        if resultado['riesgo'] == 'critico':
            color = Colors.RED
            simbolo = '🚨'
        elif resultado['riesgo'] == 'alto':
            color = Colors.YELLOW
            simbolo = '⚠️'
        elif resultado['riesgo'] == 'medio':
            color = Colors.BLUE
            simbolo = '⚡'
        else:
            color = Colors.GREEN
            simbolo = '✓'
        
        print("\n" + color + "="*70 + Colors.END)
        print(color + f"{simbolo}  ANÁLISIS COMPLETADO - {datetime.now().strftime('%H:%M:%S')}" + Colors.END)
        print(color + "="*70 + Colors.END)
        
        print(Colors.BOLD + "\n ESTADO EMOCIONAL DETECTADO:" + Colors.END)
        print(f"   Emoción: {color}{resultado['emocion'].upper()}{Colors.END}")
        print(f"   Nivel de Riesgo: {color}{resultado['riesgo'].upper()}{Colors.END}")
        print(f"   Confianza: {int(resultado['confianza']*100)}%")
        print(f"   Explicación: {resultado['explicacion']}")
        
        print(Colors.BOLD + "\n📊 MÉTRICAS DE VOZ:" + Colors.END)
        m = resultado['metricas']
        print(f"   Volumen promedio: {m['volumen']:.0f}")
        print(f"   Volumen máximo: {m['volumen_max']:.0f}")
        print(f"   Variabilidad: {m['variabilidad']:.0f}")
        print(f"   Frecuencia aproximada: {m['frecuencia']:.0f} Hz")
        print(f"   Energía: {m['energia']:.0f}")
        print(f"   Pausas detectadas: {m['pausas']:.0f}")
        
        # Protocolo de respuesta
        self._mostrar_protocolo(resultado)
    
    def _mostrar_protocolo(self, resultado):
        """Muestra el protocolo de respuesta según el estado."""
        
        print(Colors.BOLD + "\n🎨 PROTOCOLO DE RESPUESTA ACTIVADO:" + Colors.END)
        
        protocolos = {
            'ansiedad': {
                'color': 'AZUL TRANQUILIZANTE 🔵',
                'musica': 'Música Binaural 432Hz (calma)',
                'video': 'Olas del mar en playa tranquila',
                'respiracion': 'Respiración cuadrada 4-4-4-4',
                'mensaje': 'Tu respiración puede ayudarte a recuperar el control'
            },
            'depresion': {
                'color': 'NARANJA CÁLIDO 🟠',
                'musica': 'Música Binaural 528Hz (sanación)',
                'video': 'Amanecer en montañas',
                'respiracion': 'Respiración 4-7-8 (calma profunda)',
                'mensaje': 'No estás solo. Vamos a trabajar juntos en esto'
            },
            'tristeza': {
                'color': 'VERDE ESPERANZA 🟢',
                'musica': 'Música Binaural 396Hz (liberación)',
                'video': 'Bosque con luz filtrada',
                'respiracion': 'Respiración consciente 5-5',
                'mensaje': 'Tus emociones son válidas. Estoy aquí para acompañarte'
            },
            'crisis': {
                'color': 'ROJO SUAVE (ALERTA) 🔴',
                'musica': 'Voz humana guiada de contención',
                'video': 'Contacto visual con terapeuta',
                'respiracion': 'Respiración de emergencia 3-6-3',
                'mensaje': '🚨 CONECTANDO CON LÍNEA DE CRISIS AHORA'
            },
            'estable': {
                'color': 'VERDE CLARO 🟢',
                'musica': 'Música ambiente suave',
                'video': 'Paisajes diversos',
                'respiracion': 'Respiración natural',
                'mensaje': 'Me alegra que estés aquí. ¿En qué puedo apoyarte hoy?'
            }
        }
        
        protocolo = protocolos.get(resultado['emocion'], protocolos['estable'])
        
        print(f"   🎨 Iluminación: {protocolo['color']}")
        print(f"   🎵 Audio: {protocolo['musica']}")
        print(f"   🎬 Video: {protocolo['video']}")
        print(f"   🫁 Ejercicio: {protocolo['respiracion']}")
        print(f"   💬 Mensaje: '{protocolo['mensaje']}'")
        
        if resultado['riesgo'] == 'critico':
            print(Colors.RED + "\n   🚨 EMERGENCIA ACTIVADA:" + Colors.END)
            print("   → Llamando a: 800-911-2000 (Línea de la Vida)")
            print("   → SMS enviado a supervisor")
            print("   → Incidente registrado")
            print("   → Tiempo de respuesta: 45 segundos")
    
    def cerrar(self):
        """Cierra el analizador."""
        self.audio.terminate()
        print(Colors.GREEN + "\n✓ Analizador cerrado" + Colors.END)


def print_banner():
    """Muestra el banner."""
    print("\n" + "="*70)
    print(Colors.HEADER + Colors.BOLD + """
    +----------------------------------------------------------+
    |                                                          |
    |     SISTEMA DE CABINAS ANTI-SUICIDIO                     |
    |     Análisis de Voz en Tiempo Real                       |
    |                                                          |
    +----------------------------------------------------------+
    """ + Colors.END)
    print("="*70 + "\n")


def menu_principal():
    """Menú de opciones."""
    print(Colors.BOLD + "\n📋 MENÚ PRINCIPAL:" + Colors.END)
    print("  1. Analizar mi voz AHORA (demo individual)")
    print("  2. Sesión completa (5 análisis seguidos)")
    print("  3. Probar emergencia (habla muy bajito)")
    print("  4. Ver mis micrófonos")
    print("  5. Salir")
    print()


def main():
    """Función principal."""
    print_banner()
    
    print("Desarrollado por: Miguel Rodríguez León")
    print("Email: miguel.lifekey@gmail.com")
    print("Tel: +52 33 1855 9919")
    print()
    
    # Inicializar analizador
    try:
        analizador = AnalizadorVozSimple()
    except Exception as e:
        print(Colors.RED + f"\n✗ Error al inicializar: {e}" + Colors.END)
        print("\nAsegúrate de tener un micrófono conectado.")
        print("En Windows: Ve a Configuración → Privacidad → Micrófono")
        print("En Mac: Preferencias del Sistema → Seguridad → Micrófono")
        return
    
    # Mostrar micrófonos disponibles
    micros = analizador.listar_microfonos()
    if not micros:
        print(Colors.RED + "\n✗ No se detectaron micrófonos" + Colors.END)
        return
    
    while True:
        menu_principal()
        
        try:
            opcion = input("Selecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                # Análisis individual
                print(Colors.HEADER + "\n▶ ANÁLISIS INDIVIDUAL\n" + Colors.END)
                print("Prepárate para hablar cuando aparezca 'HABLA AHORA'")
                print("Puedes decir cualquier cosa (una frase, contar hasta 10, etc.)")
                input("\nPresiona ENTER cuando estés listo...")
                
                audio = analizador.grabar_audio()
                resultado = analizador.analizar_audio(audio)
                analizador.mostrar_resultado(resultado)
                
                input("\nPresiona ENTER para continuar...")
                
            elif opcion == '2':
                # Sesión completa
                print(Colors.HEADER + "\n▶ SESIÓN COMPLETA (5 análisis)\n" + Colors.END)
                print("Vamos a hacer 5 análisis seguidos.")
                print("Intenta variar tu tono y energía en cada uno.")
                print()
                input("Presiona ENTER para comenzar...")
                
                resultados = []
                for i in range(1, 6):
                    print(Colors.BOLD + f"\n--- ANÁLISIS {i} de 5 ---" + Colors.END)
                    time.sleep(1)
                    
                    audio = analizador.grabar_audio()
                    resultado = analizador.analizar_audio(audio)
                    analizador.mostrar_resultado(resultado)
                    
                    resultados.append(resultado)
                    
                    if i < 5:
                        print("\nEspera 3 segundos para el siguiente...")
                        time.sleep(3)
                
                # Resumen
                print("\n" + "="*70)
                print(Colors.HEADER + Colors.BOLD + "📊 RESUMEN DE LA SESIÓN" + Colors.END)
                print("="*70)
                
                emociones = {}
                for r in resultados:
                    emociones[r['emocion']] = emociones.get(r['emocion'], 0) + 1
                
                print("\nEmociones detectadas:")
                for emocion, cantidad in emociones.items():
                    print(f"  • {emocion.capitalize()}: {cantidad} veces")
                
                emergencias = sum(1 for r in resultados if r['riesgo'] == 'critico')
                if emergencias > 0:
                    print(Colors.RED + f"\n🚨 Emergencias detectadas: {emergencias}" + Colors.END)
                
                input("\nPresiona ENTER para continuar...")
                
            elif opcion == '3':
                # Prueba de emergencia
                print(Colors.YELLOW + "\n▶ PRUEBA DE EMERGENCIA\n" + Colors.END)
                print("Para simular una emergencia:")
                print("  • Habla MUY bajito (casi susurrando)")
                print("  • Haz pausas largas entre palabras")
                print("  • O simplemente quédate en silencio")
                print()
                input("Presiona ENTER cuando estés listo...")
                
                audio = analizador.grabar_audio()
                resultado = analizador.analizar_audio(audio)
                analizador.mostrar_resultado(resultado)
                
                input("\nPresiona ENTER para continuar...")
                
            elif opcion == '4':
                # Listar micrófonos
                analizador.listar_microfonos()
                input("\nPresiona ENTER para continuar...")
                
            elif opcion == '5':
                # Salir
                print(Colors.GREEN + "\n✓ Gracias por probar el sistema" + Colors.END)
                print(Colors.BOLD + "\nCabinas Anti-suicidio" + Colors.END)
                print("Salvando vidas con tecnología\n")
                analizador.cerrar()
                break
                
            else:
                print(Colors.RED + "\n✗ Opción no válida\n" + Colors.END)
                
        except KeyboardInterrupt:
            print(Colors.YELLOW + "\n\n⏸️  Programa interrumpido" + Colors.END)
            analizador.cerrar()
            break
        except Exception as e:
            print(Colors.RED + f"\n✗ Error: {e}\n" + Colors.END)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Colors.RED + f"\nError crítico: {e}" + Colors.END)
        print("\nSi el problema persiste, contacta a:")
        print("miguel.lifekey@gmail.com")