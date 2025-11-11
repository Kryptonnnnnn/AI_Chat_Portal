/**
 * Export utility functions for conversations
 * Supports JSON, Markdown, and Text formats
 */

export const exportToJSON = (conversation) => {
    const dataStr = JSON.stringify(conversation, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversation-${conversation.id}-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  export const exportToMarkdown = (conversation) => {
    let markdown = `# ${conversation.title}\n\n`;
    markdown += `**Created:** ${new Date(conversation.created_at).toLocaleString()}\n`;
    markdown += `**Status:** ${conversation.status}\n`;
    
    if (conversation.ended_at) {
      markdown += `**Ended:** ${new Date(conversation.ended_at).toLocaleString()}\n`;
    }
    
    if (conversation.duration) {
      markdown += `**Duration:** ${conversation.duration} minutes\n`;
    }
    
    if (conversation.summary) {
      markdown += `\n## Summary\n\n${conversation.summary}\n`;
    }
    
    if (conversation.topics && conversation.topics.length > 0) {
      markdown += `\n## Topics\n\n${conversation.topics.map(t => `- ${t}`).join('\n')}\n`;
    }
    
    if (conversation.sentiment) {
      markdown += `\n## Sentiment\n\n${conversation.sentiment}\n`;
    }
    
    markdown += `\n## Conversation\n\n`;
    
    conversation.messages.forEach((msg) => {
      const sender = msg.sender === 'user' ? '👤 **You**' : '🤖 **AI Assistant**';
      const time = new Date(msg.timestamp).toLocaleTimeString();
      markdown += `### ${sender} _(${time})_\n\n${msg.content}\n\n---\n\n`;
    });
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversation-${conversation.id}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  export const exportToText = (conversation) => {
    let text = `${conversation.title}\n`;
    text += `${'='.repeat(conversation.title.length)}\n\n`;
    text += `Created: ${new Date(conversation.created_at).toLocaleString()}\n`;
    text += `Status: ${conversation.status}\n`;
    
    if (conversation.ended_at) {
      text += `Ended: ${new Date(conversation.ended_at).toLocaleString()}\n`;
    }
    
    if (conversation.duration) {
      text += `Duration: ${conversation.duration} minutes\n`;
    }
    
    if (conversation.summary) {
      text += `\nSummary:\n${conversation.summary}\n`;
    }
    
    if (conversation.topics && conversation.topics.length > 0) {
      text += `\nTopics: ${conversation.topics.join(', ')}\n`;
    }
    
    if (conversation.sentiment) {
      text += `Sentiment: ${conversation.sentiment}\n`;
    }
    
    text += `\nMessages:\n${'='.repeat(70)}\n\n`;
    
    conversation.messages.forEach((msg) => {
      const sender = msg.sender === 'user' ? 'You' : 'AI Assistant';
      const time = new Date(msg.timestamp).toLocaleTimeString();
      text += `[${time}] ${sender}:\n${msg.content}\n\n${'-'.repeat(70)}\n\n`;
    });
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversation-${conversation.id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  export const exportToPDF = async (conversation) => {
    // This would require a PDF library like jsPDF
    // For now, we'll create a printable HTML version
    const printWindow = window.open('', '_blank');
    
    let html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${conversation.title}</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
          h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
          .meta { background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; }
          .message { margin: 20px 0; padding: 15px; border-left: 4px solid #2563eb; background: #f9fafb; }
          .user { border-left-color: #2563eb; }
          .ai { border-left-color: #8b5cf6; }
          .sender { font-weight: bold; color: #1f2937; }
          .time { color: #6b7280; font-size: 0.875rem; }
          .topics { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
          .topic { background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 16px; font-size: 0.875rem; }
          @media print { body { margin: 0; } }
        </style>
      </head>
      <body>
        <h1>${conversation.title}</h1>
        <div class="meta">
          <p><strong>Created:</strong> ${new Date(conversation.created_at).toLocaleString()}</p>
          <p><strong>Status:</strong> ${conversation.status}</p>
          ${conversation.duration ? `<p><strong>Duration:</strong> ${conversation.duration} minutes</p>` : ''}
          ${conversation.summary ? `<p><strong>Summary:</strong> ${conversation.summary}</p>` : ''}
          ${conversation.sentiment ? `<p><strong>Sentiment:</strong> ${conversation.sentiment}</p>` : ''}
          ${conversation.topics && conversation.topics.length > 0 ? `
            <p><strong>Topics:</strong></p>
            <div class="topics">
              ${conversation.topics.map(t => `<span class="topic">${t}</span>`).join('')}
            </div>
          ` : ''}
        </div>
        <h2>Conversation</h2>
        ${conversation.messages.map(msg => `
          <div class="message ${msg.sender}">
            <div class="sender">${msg.sender === 'user' ? '👤 You' : '🤖 AI Assistant'}</div>
            <div class="time">${new Date(msg.timestamp).toLocaleString()}</div>
            <p>${msg.content.replace(/\n/g, '<br>')}</p>
          </div>
        `).join('')}
      </body>
      </html>
    `;
    
    printWindow.document.write(html);
    printWindow.document.close();
    
    // Auto-print after content loads
    printWindow.onload = function() {
      printWindow.print();
    };
  };