import React, { useState } from 'react';
import ProductGrid from './ProductGrid';
import HistoryPanel from './HistoryPanel';
import { Product } from './types';

interface HistoryItem {
  id: string;
  timestamp: Date;
  query: string;
  products: Product[];
}

interface ProductPaneProps {
  currentProducts: Product[];
  history: HistoryItem[];
  currentQuery?: string;
  onProductClick?: (product: Product) => void;
}

const ProductPane: React.FC<ProductPaneProps> = ({ 
  currentProducts, 
  history, 
  currentQuery,
  onProductClick 
}) => {
  const [activeTab, setActiveTab] = useState<'current' | 'history'>('current');

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Product Pane Header */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 p-4 text-white">
        <h2 className="text-xl font-bold">Product Recommendations</h2>
        <p className="text-green-100 text-sm">AI-powered shopping suggestions</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'current'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('current')}
        >
          Current Results
        </button>
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'history'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
      </div>

      {/* Product Content - Scrollable area */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'current' ? (
          <div className="h-full flex flex-col">
            {currentQuery && (
              <div className="p-4 border-b border-gray-200 bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-700">
                  Results for: "{currentQuery}"
                </h3>
                <div className="text-sm text-gray-600 mt-1">
                  Found {currentProducts.length} product{currentProducts.length !== 1 ? 's' : ''}
                </div>
              </div>
            )}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
              {currentProducts.length > 0 ? (
                <ProductGrid 
                  products={currentProducts}
                  onProductClick={onProductClick}
                />
              ) : (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                  <p className="text-gray-500">Search for products to see recommendations</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <h3 className="text-lg font-semibold text-gray-700">Search History</h3>
              <div className="text-sm text-gray-600 mt-1">
                {history.length} previous search{history.length !== 1 ? 'es' : ''}
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
              <HistoryPanel 
                history={history}
                onProductClick={onProductClick}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductPane;