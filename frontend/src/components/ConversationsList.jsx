import React, { useState, useEffect } from 'react';
import { MessageSquare, Clock, Calendar, Search, Trash2, Eye } from 'lucide-react';
import { conversationAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

const ConversationsList = () => {
  const [conversations, setConversations] = useState([]);
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    filterConversations();
  }, [searchQuery, statusFilter, conversations]);

  const loadConversations = async () => {
    setIsLoading(true);
    try {
      const data = await conversationAPI.getAll();
      setConversations(data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterConversations = () => {
    let filtered = [...conversations];

    if (statusFilter !== 'all') {
      filtered = filtered.filter((conv) => conv.status === statusFilter);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (conv) =>
          conv.title.toLowerCase().includes(query) ||
          conv.topics?.some((topic) => topic.toLowerCase().includes(query))
      );
    }

    setFilteredConversations(filtered);
  };

  const handleViewConversation = (id) => {
    navigate(`/chat/${id}`);
  };

  const handleDeleteConversation = async (id, title) => {
    if (!window.confirm(`Delete "${title}"?`)) return;

    try {
      await conversationAPI.deleteConversation(id);
      setConversations((prev) => prev.filter((conv) => conv.id !== id));
    } catch (error) {
      console.error('Error deleting conversation:', error);
      alert('Failed to delete conversation.');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">Conversations</h1>
        
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="ended">Ended</option>
          </select>
        </div>
      </div>

      <div className="px-6 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="text-center py-20">
            <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              {searchQuery || statusFilter !== 'all'
                ? 'No conversations match your filters'
                : 'No conversations yet'}
            </p>
            <button
              onClick={() => navigate('/chat')}
              className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Start New Conversation
            </button>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
              Showing {filteredConversations.length} of {conversations.length} conversations
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-white flex-1 pr-2">
                        {conversation.title}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          conversation.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {conversation.status}
                      </span>
                    </div>

                    {conversation.latest_message && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                        {conversation.latest_message.content}
                      </p>
                    )}

                    {conversation.topics && conversation.topics.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {conversation.topics.slice(0, 3).map((topic, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-4">
                      <div className="flex items-center gap-1">
                        <MessageSquare className="w-4 h-4" />
                        {conversation.message_count} messages
                      </div>
                      {conversation.duration && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {Math.round(conversation.duration)} min
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-1 text-xs text-gray-400 mb-4">
                      <Calendar className="w-3 h-3" />
                      {formatDate(conversation.created_at)} at {formatTime(conversation.created_at)}
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleViewConversation(conversation.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
                      >
                        <Eye className="w-4 h-4" />
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteConversation(conversation.id, conversation.title)}
                        className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ConversationsList;