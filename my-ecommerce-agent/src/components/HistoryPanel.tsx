import React, { useState } from 'react';
import ProductGrid from './ProductGrid';
import { Product } from './types';

interface HistoryItem {
  id: string;
  timestamp: Date;
  query: string;
  products: Product[];
}

interface HistoryPanelProps {
  history: HistoryItem[];
  onProductClick?: (product: Product) => void;
  onHistoryItemClick?: (item: HistoryItem) => void;
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({ history, onProductClick, onHistoryItemClick }) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleItem = (id: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  return (
    <div className="h-full flex flex-col">
      {history.length === 0 ? (
        <div className="text-center py-8 text-gray-500 flex-1 flex items-center justify-center">
          <div>
            <p>No search history yet</p>
            <p className="text-sm mt-2">Your previous searches will appear here</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4 flex-1 overflow-y-auto">
          {history.map((item) => (
            <div key={item.id} className="border border-gray-200 rounded-lg bg-white overflow-hidden">
              <button
                onClick={() => {
                  toggleItem(item.id);
                  if (onHistoryItemClick) {
                    onHistoryItemClick(item);
                  }
                }}
                className="w-full flex justify-between items-center p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
              >
                <div>
                  <h3 className="font-medium text-gray-800">{item.query}</h3>
                  <p className="text-sm text-gray-500">{formatDate(item.timestamp)}</p>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-500 mr-2">{item.products.length} products</span>
                  <svg 
                    className={`w-5 h-5 text-gray-500 transition-transform ${expandedItems.has(item.id) ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>
              
              {expandedItems.has(item.id) && (
                <div className="p-4 border-t border-gray-200 max-h-96 overflow-y-auto">
                  <ProductGrid 
                    products={item.products} 
                    onProductClick={onProductClick}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HistoryPanel;