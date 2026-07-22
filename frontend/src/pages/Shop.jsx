import { useEffect, useState } from 'react'
import { Search, SlidersHorizontal } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import api from '../api'
import ProductCard from '../components/ProductCard'

export default function Shop() {
  const [params, setParams] = useSearchParams(); const [products, setProducts] = useState([]); const [categories, setCategories] = useState([]); const [loading, setLoading] = useState(true); const [count, setCount] = useState(0)
  const category = params.get('category') || ''; const query = params.get('q') || ''; const ordering = params.get('ordering') || '-created_at'
  useEffect(() => { api.get('/categories/').then(r => setCategories(r.data)) }, [])
  useEffect(() => { setLoading(true); api.get('/products/', { params: { category, q: query, ordering, page_size: 100 } }).then(r => { setProducts(r.data.results || r.data); setCount(r.data.count ?? r.data.length) }).finally(() => setLoading(false)) }, [category, query, ordering])
  const change = (key, value) => { const next = new URLSearchParams(params); value ? next.set(key, value) : next.delete(key); setParams(next) }
  return <div className="container page"><div className="shop-hero"><span className="kicker">The project catalog</span><h1>Build your next breakthrough</h1><p>Explore 100 practical kits across ten high-impact technology tracks.</p></div><div className="shop-toolbar"><div className="searchbox"><Search /><input value={query} onChange={e => change('q', e.target.value)} placeholder="Search projects, skills, categories…" /></div><div className="filter-select"><SlidersHorizontal /><select value={ordering} onChange={e => change('ordering', e.target.value)}><option value="-created_at">Newest</option><option value="price">Price: low to high</option><option value="-price">Price: high to low</option><option value="-rating">Top rated</option><option value="name">Name</option></select></div></div><div className="chips"><button className={!category ? 'active' : ''} onClick={() => change('category', '')}>All</button>{categories.map(c => <button key={c.id} className={category === c.slug ? 'active' : ''} onClick={() => change('category', c.slug)}>{c.name}</button>)}</div><div className="results-line"><b>{count} projects</b><span>Prices include applicable tax</span></div>{loading ? <div className="loader" /> : products.length ? <div className="product-grid">{products.map(p => <ProductCard key={p.id} product={p} />)}</div> : <div className="empty"><h2>No matching projects</h2><p>Try a broader search or a different category.</p></div>}</div>
}

