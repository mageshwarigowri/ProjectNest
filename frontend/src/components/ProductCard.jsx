import { Link } from 'react-router-dom'
import { ArrowUpRight, ShoppingBag, Star } from 'lucide-react'
import { useStore } from '../StoreContext'

export default function ProductCard({ product }) {
  const { addToCart } = useStore()
  return <article className="product-card">
    <Link to={`/products/${product.slug}`} className="product-image"><img src={product.image_url} alt="" loading="lazy" /><span className={`stock ${product.stock_label.toLowerCase().replaceAll(' ', '-')}`}>{product.stock_label}</span>{product.discount_percent > 0 && <b className="discount">-{product.discount_percent}%</b>}</Link>
    <div className="product-info"><small>{product.category_name}</small><Link to={`/products/${product.slug}`}><h3>{product.name}<ArrowUpRight size={17} /></h3></Link><div className="rating"><Star size={14} fill="currentColor" /> {product.rating} <span>({product.review_count})</span></div><div className="price-row"><div><strong>₹{Number(product.sale_price).toLocaleString('en-IN')}</strong>{product.discount_percent > 0 && <del>₹{Number(product.price).toLocaleString('en-IN')}</del>}</div><button onClick={() => addToCart(product)} disabled={product.stock_label === 'Out of stock'} aria-label={`Add ${product.name} to cart`}><ShoppingBag size={18} /></button></div></div>
  </article>
}

