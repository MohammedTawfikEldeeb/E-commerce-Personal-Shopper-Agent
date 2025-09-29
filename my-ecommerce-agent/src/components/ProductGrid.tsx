import React from 'react';
import ProductCard from './ProductCard';
import { Product } from './types';

interface ProductGridProps {
  products: Product[];
  title?: string;
  onProductClick?: (product: Product) => void;
}

const ProductGrid: React.FC<ProductGridProps> = ({ products, title, onProductClick }) => {
  return (
    <div className="mb-8">
      {title && (
        <h3 className="text-lg font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200">
          {title}
        </h3>
      )}
      
      {products.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No products found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product, index) => (
            <ProductCard 
              key={index}
              product={product}
              onProductClick={onProductClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductGrid;