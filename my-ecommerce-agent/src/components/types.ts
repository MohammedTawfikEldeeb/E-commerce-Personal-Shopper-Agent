export interface ProductMeta {
  title?: string;
  category?: string;
  sub_category?: string;
  sale_price?: number;
  original_price?: number;
  currency?: string;
  available_sizes?: string;
  product_url?: string;
  image_url?: string;
  product_details_json?: string;
  // Legacy fields for backward compatibility
  selling_price?: number;
  actual_price?: number;
  discount_percentage?: string | number;
  images?: string[];
  url?: string;
}

export interface Product {
  metadata: ProductMeta;
  content?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}