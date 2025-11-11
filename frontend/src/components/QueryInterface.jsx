import React, { useState } from 'react';
import { Search, Loader2, Calendar, MessageSquare, TrendingUp } from 'lucide-react';
import { conversationAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handleSubmitQuery = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const response = await conversationAPI.queryConversations(query);
      setResult(response);
    } catch (error) {
      console.error('Error querying conversations:', error);
      alert('Failed to query conversations.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewConversation = (id) => {
    navigate(`/chat/${id}`);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const suggestedQueries = [
    'What topics did we discuss most?',
    'Summarize all technical conversations',
    'What decisions were made?',
    'Find conversations about project planning',
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-2">
          Conversation Intelligence
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Ask questions about your past conversations
        </p>
      </div>

      <div className="px-6 py-6 max-w-6xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <form onSubmit={handleSubmitQuery}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Ask a question
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="What did we discuss about..."
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Search Conversations
                </>
              )}
            </button>
          </form>

          {!result && (
            <div className="mt-6">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Try these queries:
              </p>
              <div className="flex flex-wrap gap-2">
                {suggestedQueries.map((suggested, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuery(suggested)}
                    className="px-3 py-1 bg-gray-100 text-gray-700 dark:text-gray-300 text-sm rounded-full hover:bg-gray-200"
                  >
                    {suggested}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {result && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
                    AI Analysis
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                    {result.response}
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-500">
                  Searched {result.total_searched} conversations • Found{' '}
                  {result.relevant_conversations.length} relevant results
                </p>
              </div>
            </div>

            {result.relevant_conversations.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
                  Relevant Conversations
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.relevant_conversations.map((conv) => (
                    <div
                      key={conv.id}
                      className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-lg font-semibold text-gray-800 dark:text-white flex-1">
                          {conv.title}
                        </h4>
                        <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                          {Math.round(conv.relevance_score * 100)}% match
                        </span>
                      </div>

                      {conv.summary && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-3">
                          {conv.summary}
                        </p>
                      )}

                      {conv.topics && conv.topics.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {conv.topics.slice(0, 3).map((topic, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded"
                            >
                              {topic}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(conv.created_at)}
                        </div>
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {conv.message_count} messages
                        </div>
                      </div>

                      <button
                        onClick={() => handleViewConversation(conv.id)}
                        className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
                      >
                        View Conversation
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryInterface;