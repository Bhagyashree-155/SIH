import React, { useState, useRef, useEffect } from "react";
import { Box, TextField, Button, Typography, Paper, Avatar, IconButton, Tooltip } from '@mui/material';
import { Send as SendIcon, SmartToy as AIIcon, VolumeUp as VolumeUpIcon, VolumeOff as VolumeOffIcon, Mic as MicIcon, MicOff as MicOffIcon } from '@mui/icons-material';

export default function AIChat() {
  const [messages, setMessages] = useState([
    {
      role: "ai",
      text: "Hello! I'm your AI assistant for the POWERGRID ticketing system. I can help you with:\n• Creating and managing tickets\n• Finding solutions in the knowledge base\n• Routing tickets to the right team\n• Providing status updates\n\nHow can I assist you today?"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  const chatEndRef = useRef(null);
  const apiKey = "AIzaSyBgz_NoFRYhbhHnYgl7PLs8fHm7ZcG60l4"; // ⚠️ Replace with your actual key

  // Auto scroll to bottom when messages update
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Check for speech recognition support
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setSpeechSupported(true);
    }
  }, []);

  // 🔊 Function to speak text
  const speakText = (text) => {
    if (!text.trim()) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US"; // Change language if needed
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    speechSynthesis.speak(utterance);
  };

  // 🔇 Function to stop voice
  const stopSpeaking = () => {
    speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  // 🎤 Function to start voice input
  const startVoiceInput = () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please allow microphone access and try again.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  // 🛑 Function to stop voice input
  const stopVoiceInput = () => {
    setIsListening(false);
    // Note: SpeechRecognition doesn't have a direct stop method in some browsers
    // The recognition will stop automatically on error or result
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    const newMessages = [...messages, { role: "user", text: userMessage }];
    setMessages(newMessages);

    try {
      const response = await fetch(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=" +
          apiKey,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: userMessage }] }],
          }),
        }
      );

      const data = await response.json();
      const aiText =
        data?.candidates?.[0]?.content?.parts?.[0]?.text || "⚠️ No response";

      setMessages((prev) => [...prev, { role: "ai", text: aiText }]);
      
      // Automatically speak AI response
      setTimeout(() => speakText(aiText), 500);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "⚠️ Error contacting AI service. Please try again." },
      ]);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      maxHeight: '600px',
      bgcolor: '#f8fafc',
      borderRadius: 2,
      overflow: 'hidden'
    }}>
      {/* Chat Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: '1px solid #e5e7eb',
        bgcolor: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ 
            bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            width: 40,
            height: 40
          }}>
            <AIIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
              AI Assistant
            </Typography>
            <Typography variant="caption" sx={{ color: '#10b981' }}>
              ● Online
            </Typography>
          </Box>
        </Box>
        
        {/* Voice Controls */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title={isSpeaking ? "Stop speaking" : "Speak last AI message"}>
            <IconButton
              onClick={isSpeaking ? stopSpeaking : () => {
                const lastAIMessage = messages.filter(m => m.role === 'ai').pop();
                if (lastAIMessage) speakText(lastAIMessage.text);
              }}
              sx={{
                color: isSpeaking ? '#ef4444' : '#3b82f6',
                '&:hover': {
                  bgcolor: isSpeaking ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.1)'
                }
              }}
            >
              {isSpeaking ? <VolumeOffIcon /> : <VolumeUpIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Chat Messages */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {messages.map((msg, i) => (
          <Box key={i} sx={{ 
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            mb: 1
          }}>
            <Box sx={{ 
              display: 'flex',
              alignItems: 'flex-start',
              gap: 1,
              maxWidth: '80%'
            }}>
              <Paper sx={{
                p: 2,
                borderRadius: msg.role === 'user' ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
                bgcolor: msg.role === 'user' ? '#3b82f6' : '#f1f5f9',
                color: msg.role === 'user' ? 'white' : '#475569',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                flex: 1
              }}>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </Typography>
              </Paper>
              
              {/* Voice button for AI messages */}
              {msg.role === 'ai' && (
                <Tooltip title="Speak this message">
                  <IconButton
                    size="small"
                    onClick={() => speakText(msg.text)}
                    sx={{
                      color: '#3b82f6',
                      mt: 0.5,
                      '&:hover': {
                        bgcolor: 'rgba(59, 130, 246, 0.1)'
                      }
                    }}
                  >
                    <VolumeUpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>
        ))}
        {loading && (
          <Box sx={{ 
            display: 'flex',
            justifyContent: 'flex-start',
            mb: 1
          }}>
            <Paper sx={{
              p: 2,
              borderRadius: '12px 12px 12px 4px',
              bgcolor: '#f1f5f9',
              color: '#475569'
            }}>
              <Typography variant="body2">
                AI is typing...
              </Typography>
            </Paper>
          </Box>
        )}
        <div ref={chatEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid #e5e7eb',
        bgcolor: 'white',
        display: 'flex',
        gap: 1,
        alignItems: 'flex-end'
      }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder={isListening ? "Listening... Speak now..." : "Ask me anything about tickets or IT issues..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading || isListening}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
              backgroundColor: isListening ? '#fef3c7' : 'white',
              '& fieldset': {
                borderColor: isListening ? '#f59e0b' : 'rgba(0,0,0,0.1)',
                borderWidth: isListening ? '2px' : '1px'
              },
              '&:hover fieldset': {
                borderColor: isListening ? '#f59e0b' : '#3b82f6'
              },
              '&.Mui-focused fieldset': {
                borderColor: isListening ? '#f59e0b' : '#3b82f6'
              }
            }
          }}
        />
        
        {/* Voice Input Button */}
        {speechSupported && (
          <Tooltip title={isListening ? "Stop listening" : "Start voice input"}>
            <IconButton
              onClick={isListening ? stopVoiceInput : startVoiceInput}
              disabled={loading}
              sx={{
                color: isListening ? '#ef4444' : '#3b82f6',
                bgcolor: isListening ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                '&:hover': {
                  bgcolor: isListening ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)'
                },
                '&:disabled': {
                  color: '#9ca3af',
                  bgcolor: 'rgba(156, 163, 175, 0.1)'
                },
                mb: 0.5
              }}
            >
              {isListening ? <MicOffIcon /> : <MicIcon />}
            </IconButton>
          </Tooltip>
        )}
        
        <Button
          variant="contained"
          onClick={sendMessage}
          disabled={!input.trim() || loading || isListening}
          sx={{
            minWidth: 'auto',
            px: 2,
            py: 1.5,
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)'
            },
            '&:disabled': {
              background: '#e5e7eb',
              color: '#9ca3af'
            }
          }}
        >
          <SendIcon />
        </Button>
      </Box>
    </Box>
  );
}
