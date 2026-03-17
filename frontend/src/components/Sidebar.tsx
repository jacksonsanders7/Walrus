import React from 'react';
import './Sidebar.css';

interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

interface Props {
  conversations: Record<string, Conversation>;
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

const Sidebar: React.FC<Props> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <button onClick={onNewConversation} className="new-chat-btn">
          + New Chat
        </button>
      </div>

      <div className="conversations-list">
        {Object.values(conversations).map((conv) => (
          <div
            key={conv.id}
            className={`conversation-item ${
              currentConversationId === conv.id ? 'active' : ''
            }`}
          >
            <div
              className="conversation-link"
              onClick={() => onSelectConversation(conv.id)}
            >
              {conv.title}
            </div>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteConversation(conv.id);
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
