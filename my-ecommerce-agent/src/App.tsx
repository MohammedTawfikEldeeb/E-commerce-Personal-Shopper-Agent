// src/App.tsx
import React, { useState, useEffect } from 'react';
import ChatPane from './components/ChatPane';
import ProductPane from './components/ProductPane';
import { Message, Product } from './components/types';
import './App.css';

// Define HistoryItem interface
interface HistoryItem {
  id: string;
  timestamp: Date;
  query: string;
  products: Product[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentProducts, setCurrentProducts] = useState<Product[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleSendMessage = async (message: string) => {
    const userMessage: Message = { role: 'user', content: message };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setIsLoading(true);
    setCurrentQuery(message);

    // Add thinking message
    setMessages(prev => [...prev, { role: 'assistant', content: 'Thinking...' }]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: message,
          session_id: sessionId || undefined
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        lastMessage.content = data.response;
        return [...prev.slice(0, -1), lastMessage];
      });
      
      // Add products if available (only for product searches)
      if (data.products && Array.isArray(data.products) && data.products.length > 0) {
        // Move current products to history
        if (currentProducts.length > 0 && currentQuery) {
          const historyItem: HistoryItem = {
            id: Date.now().toString(),
            timestamp: new Date(),
            query: currentQuery,
            products: currentProducts
          };
          setHistory(prev => [historyItem, ...prev]);
        }
        
        // Set new current products
        setCurrentProducts(data.products);
      }
      
      // Update session ID
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error contacting server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle product click (e.g., open product page)
  const handleProductClick = (product: Product) => {
    const productUrl = product.metadata?.product_url || product.metadata?.url;
    if (productUrl) {
      window.open(productUrl, '_blank');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <header className="text-center py-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          AI Shopping Assistant
        </h1>
        <p className="text-gray-600 mt-2">Your intelligent shopping companion</p>
      </header>
      
      <div className="flex flex-col lg:flex-row flex-1 gap-6 overflow-hidden">
        {/* Chat Pane - Left */}
        <div className="w-full lg:w-1/2 flex flex-col overflow-hidden">
          <ChatPane 
            messages={messages} 
            isLoading={isLoading} 
            onSendMessage={handleSendMessage} 
          />
        </div>
        
        {/* Product Pane - Right */}
        <div className="w-full lg:w-1/2 flex flex-col overflow-hidden">
          <ProductPane 
            currentProducts={currentProducts}
            history={history}
            currentQuery={currentQuery}
            onProductClick={handleProductClick}
          />
        </div>
      </div>
    </div>
  );
}

export default App;