import React from 'react';
import { Product } from './types';

interface ProductCardProps {
  product: Product;
  onProductClick?: (product: Product) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onProductClick }) => {
  const meta = product.metadata;
  
  // Get product title
  const title = meta?.title || 'Untitled Product';
  
  // Get image URL
  const imageUrl = meta?.image_url || meta?.images?.[0] || 'https://via.placeholder.com/300x200?text=No+Image';
  
  // Get current price
  const currentPrice = meta?.sale_price || meta?.selling_price;
  
  // Get original price
  const originalPrice = meta?.original_price || meta?.actual_price;
  
  // Get discount percentage
  const getDiscountPercentage = () => {
    if (!originalPrice || !currentPrice) return 0;
    if (originalPrice <= currentPrice) return 0;
    
    return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
  };
  
  const discountPercentage = getDiscountPercentage();

  // Get product URL
  const productUrl = meta?.product_url || meta?.url;

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300 flex flex-col h-full">
      {/* Product Image */}
      <div className="relative overflow-hidden">
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-48 object-cover transition-transform duration-300 hover:scale-105"
        />
        {discountPercentage > 0 && (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
            {discountPercentage}% off
          </div>
        )}
      </div>
      
      {/* Product Info */}
      <div className="flex-1 p-4 flex flex-col">
        <h3 className="font-bold text-gray-900 mb-1 line-clamp-2">{title}</h3>
        
        <div className="text-sm text-gray-500 mb-2">
          {meta?.category} {meta?.sub_category && `• ${meta.sub_category}`}
        </div>
        
        <div className="mt-auto">
          <div className="flex items-center mb-2">
            {currentPrice ? (
              <p className="text-lg font-bold text-blue-600">EGP {currentPrice}</p>
            ) : (
              <p className="text-lg font-bold text-gray-400">Price N/A</p>
            )}
            
            {originalPrice && currentPrice && originalPrice > currentPrice && (
              <p className="ml-2 text-sm text-gray-500 line-through">EGP {originalPrice}</p>
            )}
          </div>
          
          {meta?.available_sizes && (
            <p className="text-xs text-gray-600 mb-1">
              <span className="font-medium">Sizes:</span> {meta.available_sizes}
            </p>
          )}
          
          <button 
            onClick={() => {
              if (onProductClick) {
                onProductClick(product);
              } else if (productUrl) {
                window.open(productUrl, '_blank');
              }
            }}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-2 rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            View Product
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;