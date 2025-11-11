import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, MessageSquare, Clock, Calendar, Hash } from 'lucide-react';
import { conversationAPI } from '../services/api';

const AnalyticsDashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch all conversations
      const conversations = await conversationAPI.getAll();
      console.log('Loaded conversations:', conversations);
      
      if (!conversations || conversations.length === 0) {
        setStats(null);
        setIsLoading(false);
        return;
      }
      
      const analytics = calculateStats(conversations);
      setStats(analytics);
    } catch (error) {
      console.error('Error loading analytics:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (conversations) => {
    const total = conversations.length;
    const active = conversations.filter(c => c.status === 'active').length;
    const ended = conversations.filter(c => c.status === 'ended').length;
    
    const totalMessages = conversations.reduce((sum, c) => sum + (c.message_count || 0), 0);
    const avgMessages = total > 0 ? Math.round(totalMessages / total) : 0;
    
    const totalDuration = conversations
      .filter(c => c.duration)
      .reduce((sum, c) => sum + c.duration, 0);
    const avgDuration = ended > 0 ? Math.round(totalDuration / ended) : 0;
    
    // Sentiment distribution
    const sentiments = {};
    conversations.forEach(c => {
      if (c.sentiment) {
        sentiments[c.sentiment] = (sentiments[c.sentiment] || 0) + 1;
      }
    });
    
    // Topics frequency
    const topicsCount = {};
    conversations.forEach(c => {
      if (c.topics && Array.isArray(c.topics)) {
        c.topics.forEach(topic => {
          topicsCount[topic] = (topicsCount[topic] || 0) + 1;
        });
      }
    });
    
    const topTopics = Object.entries(topicsCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([topic, count]) => ({ topic, count }));
    
    // Timeline data (last 7 days)
    const timeline = getLast7Days().map(date => {
      const count = conversations.filter(c => {
        const convDate = new Date(c.created_at);
        return convDate.toDateString() === date.toDateString();
      }).length;
      return { 
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), 
        count 
      };
    });
    
    return {
      total,
      active,
      ended,
      totalMessages,
      avgMessages,
      avgDuration,
      sentiments,
      topTopics,
      timeline
    };
  };

  const getLast7Days = () => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      days.push(date);
    }
    return days;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center text-red-500">
          <p className="text-xl mb-2">Error loading analytics</p>
          <p className="text-sm">{error}</p>
          <button 
            onClick={loadAnalytics}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!stats || stats.total === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-6">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Analytics Dashboard</h1>
              <p className="text-gray-600 dark:text-gray-400">Insights from your conversations</p>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-center" style={{ height: 'calc(100vh - 200px)' }}>
          <div className="text-center">
            <BarChart3 className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-4">No analytics data available yet</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mb-6">Start having conversations to see insights here!</p>
            <button 
              onClick={() => window.location.href = '/chat'}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Start a Conversation
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-6">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Analytics Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">Insights from your conversations</p>
          </div>
        </div>
      </div>

      <div className="px-6 py-6 max-w-7xl mx-auto">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            icon={MessageSquare}
            title="Total Conversations"
            value={stats.total}
            subtitle={`${stats.active} active, ${stats.ended} ended`}
            color="blue"
          />
          <MetricCard
            icon={Hash}
            title="Total Messages"
            value={stats.totalMessages}
            subtitle={`Avg ${stats.avgMessages} per conversation`}
            color="green"
          />
          <MetricCard
            icon={Clock}
            title="Avg Duration"
            value={stats.avgDuration > 0 ? `${stats.avgDuration} min` : 'N/A'}
            subtitle="Per conversation"
            color="purple"
          />
          <MetricCard
            icon={TrendingUp}
            title="Engagement"
            value={stats.avgMessages > 10 ? 'High' : stats.avgMessages > 5 ? 'Medium' : 'Low'}
            subtitle={`${stats.avgMessages} messages avg`}
            color="orange"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Timeline Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Activity Timeline (Last 7 Days)
            </h3>
            <div className="space-y-3">
              {stats.timeline.map((day, idx) => {
                const maxCount = Math.max(...stats.timeline.map(d => d.count), 1);
                const width = (day.count / maxCount) * 100;
                return (
                  <div key={idx} className="flex items-center gap-3">
                    <span className="text-sm text-gray-600 dark:text-gray-400 w-16">{day.date}</span>
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-6 overflow-hidden">
                      <div
                        className="bg-blue-500 h-full rounded-full flex items-center justify-end pr-2"
                        style={{ width: `${Math.max(width, day.count > 0 ? 15 : 0)}%` }}
                      >
                        {day.count > 0 && (
                          <span className="text-xs text-white font-medium">{day.count}</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sentiment Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
              Sentiment Distribution
            </h3>
            {Object.keys(stats.sentiments).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(stats.sentiments).map(([sentiment, count]) => {
                  const percentage = (count / stats.ended) * 100;
                  return (
                    <div key={sentiment}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                          {sentiment}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">{count}</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${getSentimentColor(sentiment)}`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-sm">No sentiment data available yet</p>
            )}
          </div>
        </div>

        {/* Top Topics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
            Most Discussed Topics
          </h3>
          {stats.topTopics.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {stats.topTopics.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span className="text-sm text-gray-700 dark:text-gray-300 truncate">{item.topic}</span>
                  <span className="ml-2 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                    {item.count}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-sm">No topics extracted yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ icon: Icon, title, value, subtitle, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    green: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300',
    purple: 'bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-300',
    orange: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-1">{value}</h3>
      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{title}</p>
      <p className="text-xs text-gray-500 dark:text-gray-500">{subtitle}</p>
    </div>
  );
};

const getSentimentColor = (sentiment) => {
  const colors = {
    'very positive': 'bg-green-500',
    'positive': 'bg-green-400',
    'neutral': 'bg-gray-400',
    'negative': 'bg-orange-400',
    'very negative': 'bg-red-500',
  };
  return colors[sentiment] || 'bg-gray-400';
};

export default AnalyticsDashboard;
