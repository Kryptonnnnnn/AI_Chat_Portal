import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Plus, StopCircle, Download, FileJson, FileText, FileDown } from 'lucide-react';
import { conversationAPI } from '../services/api';
import { useParams, useNavigate } from 'react-router-dom';
import { exportToJSON, exportToMarkdown, exportToText, exportToPDF } from '../utils/export';

const ChatInterface = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentConvId, setCurrentConvId] = useState(id || null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConv, setIsLoadingConv] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (id) {
      loadConversation(id);
    }
  }, [id]);

  const loadConversation = async (convId) => {
    setIsLoadingConv(true);
    try {
      const data = await conversationAPI.getById(convId);
      setMessages(data.messages || []);
      setCurrentConvId(convId);
    } catch (error) {
      console.error('Error loading conversation:', error);
      alert('Failed to load conversation');
    } finally {
      setIsLoadingConv(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await conversationAPI.sendMessage(userMessage, currentConvId);
      
      if (!currentConvId && response.conversation_id) {
        setCurrentConvId(response.conversation_id);
        navigate(`/chat/${response.conversation_id}`);
      }

      setMessages((prev) => [
        ...prev,
        response.user_message,
        response.ai_response,
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setCurrentConvId(null);
    setInputMessage('');
    navigate('/chat');
  };

  const handleEndConversation = async () => {
    if (!currentConvId) return;
    
    if (!window.confirm('Are you sure you want to end this conversation?')) {
      return;
    }

    try {
      await conversationAPI.endConversation(currentConvId);
      alert('Conversation ended successfully!');
      handleNewConversation();
    } catch (error) {
      console.error('Error ending conversation:', error);
      alert('Failed to end conversation.');
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">AI Chat</h1>
          {currentConvId && (
            <p className="text-sm text-gray-500 dark:text-gray-400">Conversation #{currentConvId}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleNewConversation}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </button>
          {currentConvId && (
            <>
              <button
                onClick={handleEndConversation}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                <StopCircle className="w-4 h-4" />
                End Chat
              </button>
              <div className="relative">
                <button
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export
                </button>
                
                {showExportMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10">
                    <button
                      onClick={async () => {
                        try {
                          const conv = await conversationAPI.getById(currentConvId);
                          exportToJSON(conv);
                          setShowExportMenu(false);
                        } catch (error) {
                          console.error('Export failed:', error);
                        }
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-t-lg flex items-center gap-2 text-gray-700 dark:text-gray-300"
                    >
                      <FileJson className="w-4 h-4" />
                      Export as JSON
                    </button>
                    <button
                      onClick={async () => {
                        try {
                          const conv = await conversationAPI.getById(currentConvId);
                          exportToMarkdown(conv);
                          setShowExportMenu(false);
                        } catch (error) {
                          console.error('Export failed:', error);
                        }
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 text-gray-700 dark:text-gray-300"
                    >
                      <FileText className="w-4 h-4" />
                      Export as Markdown
                    </button>
                    <button
                      onClick={async () => {
                        try {
                          const conv = await conversationAPI.getById(currentConvId);
                          exportToText(conv);
                          setShowExportMenu(false);
                        } catch (error) {
                          console.error('Export failed:', error);
                        }
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-b-lg flex items-center gap-2 text-gray-700 dark:text-gray-300"
                    >
                      <FileDown className="w-4 h-4" />
                      Export as Text
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        {isLoadingConv ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <p className="text-xl mb-2">Start a new conversation</p>
              <p className="text-sm">Type a message below to begin</p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender === 'user' ? 'text-blue-100' : 'text-gray-400 dark:text-gray-500'
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-4">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Send
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
