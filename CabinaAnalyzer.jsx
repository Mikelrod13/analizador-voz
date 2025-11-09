import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import io from 'socket.io-client';

// La URL base de tu servidor Flask
const API_BASE_URL = 'http://localhost:5000/api';
const SOCKET_URL = 'http://localhost:5000';

// Conexión al WebSocket
const socket = io(SOCKET_URL, {
  autoConnect: false, // Evita conexión automática al cargar la página
});

function CabinaAnalyzer() {
  const [sessionId, setSessionId] = useState(null);
  const [currentEmotion, setCurrentEmotion] = useState({ emotion: 'Neutro', risk_level: 'normal', confidence: 0 });
  const [logMessages, setLogMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isEmergency, setIsEmergency] = useState(false);

  // =========================================================================
  // LOGICA DE WEBSOCKET (REAL-TIME)
  // =========================================================================

  const handleStateUpdate = useCallback((data) => {
    // Recibe el estado emocional del servidor y actualiza la UI
    setCurrentEmotion(data);
    setLogMessages((prev) => [
      ...prev,
      `[${new Date().toLocaleTimeString()}] Estado: ${data.emotion} (Riesgo: ${data.risk_level})`
    ]);
    if (data.risk_level === 'critico') {
        setIsEmergency(true);
    }
  }, []);

  const handleEmergencyAlert = useCallback((incident) => {
    setIsEmergency(true);
    setLogMessages((prev) => [
      ...prev,
      `🚨 [ALERTA CRÍTICA] Incidente ID: ${incident.incident_id}`
    ]);
  }, []);

  useEffect(() => {
    // 1. Conectar/Desconectar el Socket
    if (sessionId) {
      socket.connect();
      socket.on('state_update', handleStateUpdate);
      socket.on('emergency_alert', handleEmergencyAlert);
      socket.on('connected', () => {
        setLogMessages((prev) => [...prev, '🔌 Socket Conectado']);
      });
    } else {
      socket.off('state_update', handleStateUpdate);
      socket.off('emergency_alert', handleEmergencyAlert);
      socket.disconnect();
    }

    return () => {
      // Limpieza al desmontar o cambiar sessionId
      socket.off('state_update', handleStateUpdate);
      socket.off('emergency_alert', handleEmergencyAlert);
    };
  }, [sessionId, handleStateUpdate, handleEmergencyAlert]);
  
  // =========================================================================
  // LOGICA REST (INICIO/FIN DE SESION, CHAT)
  // =========================================================================

  const startSession = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/session/start`);
      const id = response.data.session_id;
      setSessionId(id);
      setIsEmergency(false);
      setChatHistory([]);
      setLogMessages([`✅ Sesión ${id} iniciada. Esperando datos en tiempo real...`]);
    } catch (error) {
      alert('Error al iniciar sesión. Verifica que el servidor Flask esté corriendo.');
      console.error(error);
    }
  };

  const endSession = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/session/end`);
      setLogMessages((prev) => [...prev, `🛑 Sesión ${sessionId} finalizada. (Duración: ${response.data.session_data.duration_seconds.toFixed(0)}s)`]);
      setSessionId(null);
      setIsEmergency(false);
    } catch (error) {
      alert('Error al finalizar sesión.');
      console.error(error);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !sessionId) return;

    // 1. Agregar mensaje de usuario a la UI
    const userMessage = { type: 'user', content: chatInput, timestamp: new Date().toLocaleTimeString() };
    setChatHistory((prev) => [...prev, userMessage]);
    setChatInput('');

    try {
      // 2. Enviar mensaje al servidor
      const response = await axios.post(`${API_BASE_URL}/chat`, { message: chatInput });
      const botResponse = response.data.response;

      // 3. Agregar respuesta del bot a la UI
      const botMessage = { type: 'bot', content: botResponse, timestamp: new Date().toLocaleTimeString() };
      setChatHistory((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error al enviar mensaje de chat:', error);
      const errorMessage = { type: 'error', content: 'Error de conexión con el bot.', timestamp: new Date().toLocaleTimeString() };
      setChatHistory((prev) => [...prev, errorMessage]);
    }
  };

  // =========================================================================
  // RENDERIZADO
  // =========================================================================

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Sistema de Análisis Emocional (React Client)</h1>
      
      <div style={styles.controls}>
        {!sessionId ? (
          <button onClick={startSession} style={styles.startButton}>
            ▶ INICIAR SESIÓN
          </button>
        ) : (
          <button onClick={endSession} style={styles.endButton}>
            ■ FINALIZAR SESIÓN ({sessionId})
          </button>
        )}
      </div>

      <div style={styles.statusBox}>
        <h2>ESTADO EMOCIONAL ACTUAL</h2>
        <p style={{ 
            ...styles.emotionText, 
            backgroundColor: isEmergency ? '#e74c3c' : (currentEmotion.risk_level === 'medio' ? '#f39c12' : '#2ecc71')
        }}>
          {currentEmotion.emotion.toUpperCase()}
        </p>
        <p>Nivel de Riesgo: <strong>{currentEmotion.risk_level.toUpperCase()}</strong></p>
        <p>Confianza: {(currentEmotion.confidence * 100).toFixed(0)}%</p>
      </div>

      <div style={styles.flexRow}>
        <div style={styles.chatContainer}>
            <h2>CHAT DE INTERVENCIÓN</h2>
            <div style={styles.chatHistory}>
                {chatHistory.map((msg, index) => (
                    <div key={index} style={msg.type === 'user' ? styles.userMessage : styles.botMessage}>
                        <strong>{msg.type === 'user' ? 'Tú' : 'Bot'}:</strong> {msg.content}
                        <span style={{fontSize: '0.7em', float: 'right'}}>{msg.timestamp}</span>
                    </div>
                ))}
            </div>
            <form onSubmit={handleChatSubmit} style={styles.chatForm}>
                <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder={sessionId ? 'Escribe un mensaje...' : 'Inicia sesión para chatear'}
                    disabled={!sessionId}
                    style={styles.chatInput}
                />
                <button type="submit" disabled={!sessionId} style={styles.sendButton}>
                    Enviar
                </button>
            </form>
        </div>

        <div style={styles.logContainer}>
            <h2>REGISTRO DE CONEXIÓN</h2>
            <div style={styles.logList}>
                {logMessages.map((msg, index) => (
                    <p key={index} style={{margin: '2px 0', fontSize: '0.8em', color: msg.startsWith('🚨') ? 'red' : 'inherit'}}>
                        {msg}
                    </p>
                ))}
            </div>
        </div>
      </div>
    </div>
  );
}

// Estilos básicos para la demostración
const styles = {
    container: { fontFamily: 'Arial, sans-serif', padding: '20px', maxWidth: '1200px', margin: '0 auto' },
    header: { color: '#333', borderBottom: '2px solid #ccc', paddingBottom: '10px' },
    controls: { margin: '20px 0' },
    startButton: { padding: '10px 20px', fontSize: '1em', backgroundColor: '#2ecc71', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' },
    endButton: { padding: '10px 20px', fontSize: '1em', backgroundColor: '#e74c3c', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' },
    statusBox: { 
        padding: '20px', 
        borderRadius: '8px', 
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)', 
        margin: '20px 0',
        textAlign: 'center'
    },
    emotionText: {
        fontSize: '2.5em',
        fontWeight: 'bold',
        color: 'white',
        padding: '10px 0',
        borderRadius: '5px',
        transition: 'background-color 0.5s'
    },
    flexRow: { display: 'flex', gap: '20px' },
    chatContainer: { flex: 1, border: '1px solid #ccc', borderRadius: '5px', padding: '15px', display: 'flex', flexDirection: 'column', height: '400px' },
    chatHistory: { flex: 1, overflowY: 'auto', borderBottom: '1px solid #eee', marginBottom: '10px', paddingRight: '10px' },
    userMessage: { textAlign: 'right', backgroundColor: '#d1e7dd', padding: '5px 10px', borderRadius: '5px', margin: '5px 0' },
    botMessage: { textAlign: 'left', backgroundColor: '#f8d7da', padding: '5px 10px', borderRadius: '5px', margin: '5px 0' },
    chatForm: { display: 'flex' },
    chatInput: { flex: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '5px 0 0 5px' },
    sendButton: { padding: '10px 15px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '0 5px 5px 0', cursor: 'pointer' },
    logContainer: { flex: 1, border: '1px solid #ccc', borderRadius: '5px', padding: '15px', display: 'flex', flexDirection: 'column', height: '400px' },
    logList: { flex: 1, overflowY: 'auto' }
};

export default CabinaAnalyzer;