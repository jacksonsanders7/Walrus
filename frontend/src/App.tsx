import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import ChatWindow from './components/ChatWindow';
import Sidebar from './components/Sidebar';
import MessageInput from './components/MessageInput';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [conversations, setConversations] = useState<Record<string, Conversation>>({});
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, currentConversationId]);

  const fetchConversations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations`);
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const createNewConversation = () => {
    const newId = `conv_${Date.now()}`;
    setCurrentConversationId(newId);
    fetch(`${API_BASE_URL}/api/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: newId })
    }).then(() => fetchConversations());
  };

  const sendMessage = async (message: string) => {
    if (!currentConversationId || !message.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/conversations/${currentConversationId}/messages`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        }
      );

      const data = await response.json();
      setConversations(prev => ({
        ...prev,
        [currentConversationId]: data.conversation
      }));
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/api/conversations/${id}`, {
        method: 'DELETE'
      });
      setConversations(prev => {
        const newConvs = { ...prev };
        delete newConvs[id];
        return newConvs;
      });
      if (currentConversationId === id) {
        setCurrentConversationId(null);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const currentConversation = currentConversationId ? conversations[currentConversationId] : null;

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={setCurrentConversationId}
        onNewConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
      />
      <div className="main-content">
        {currentConversation ? (
          <>
            <ChatWindow
              messages={currentConversation.messages}
              loading={loading}
              messagesEndRef={messagesEndRef}
            />
            <MessageInput
              onSendMessage={sendMessage}
              disabled={loading}
            />
          </>
        ) : (
          <div className="welcome-screen">
            <h1>ChatGPT Clone</h1>
            <p>Start a new conversation to begin chatting</p>
            <button onClick={createNewConversation} className="new-chat-btn">
              + New Chat
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
