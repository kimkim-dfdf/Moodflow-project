import { useState, useRef, useEffect } from 'react';
import api from '../api/axios';
import { Send, MessageCircle, X, Loader } from 'lucide-react';

function MusicChatbot(props) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      text: 'Hi! 🎵 I\'m your music recommendation assistant. Tell me about your mood today or what kind of music you\'re in the mood for, and I\'ll suggest some amazing songs!'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const userMessageId = Date.now();
    const userMessage = {
      id: userMessageId,
      role: 'user',
      text: inputValue
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      // Call backend API for music recommendation chat
      const response = await api.post('/api/music/chat', {
        message: inputValue,
        conversationHistory: messages
      });

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        text: response.data.reply,
        recommendations: response.data.recommendations || []
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Add error message with detailed info
      console.error('Chat error:', error);
      console.error('Error response:', error.response?.data);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        text: error.response?.data?.error || 'Sorry, an error occurred while generating recommendations. Please try again.'
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleMusicClick = (music) => {
    if (props.onSelectMusic) {
      props.onSelectMusic(music);
      setIsOpen(false);
    }
  };

  return (
    <>
      {/* Chatbot Toggle Button */}
      <button
        className="music-chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title="Music Recommendation Assistant"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chatbot Modal */}
      {isOpen && (
        <div className="music-chatbot-modal">
          <div className="music-chatbot-header">
            <h3>🎵 Music Assistant</h3>
            <button className="chatbot-close-btn" onClick={() => setIsOpen(false)}>
              <X size={20} />
            </button>
          </div>

          <div className="music-chatbot-messages">
            {messages.map((message) => (
              <div key={message.id} className={`chat-message ${message.role}`}>
                <div className="message-content">
                  <p>{message.text}</p>
                  {message.recommendations && message.recommendations.length > 0 && (
                    <div className="recommended-tracks">
                      <p className="recommendations-title">Recommended tracks:</p>
                      {message.recommendations.map((music) => (
                        <div
                          key={music.id}
                          className="recommended-track-item"
                          onClick={() => handleMusicClick(music)}
                        >
                          <div className="track-info">
                            <p className="track-title">{music.title}</p>
                            <p className="track-artist">{music.artist}</p>
                            {music.emotion && (
                              <span className="track-emotion">{music.emotion}</span>
                            )}
                          </div>
                          <span className="view-btn">View →</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div className="message-content">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="music-chatbot-input" onSubmit={handleSendMessage}>
            <input
              type="text"
              placeholder="Tell me your mood or music preference..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !inputValue.trim()}>
              {loading ? <Loader size={20} className="spinner" /> : <Send size={20} />}
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default MusicChatbot;
