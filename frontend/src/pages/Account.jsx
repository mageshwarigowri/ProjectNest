import { useEffect, useState } from 'react'
import { Coins, Download, LogOut, Package, Truck } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import { useStore } from '../StoreContext'

export default function Account() {
  const { user, authenticated, logout } = useStore(); const navigate = useNavigate(); const [orders, setOrders] = useState([])
  useEffect(() => { if (!authenticated) navigate('/login'); else api.get('/orders/?page_size=100').then(r => setOrders(r.data.results || r.data)) }, [authenticated, navigate])
  const downloadInvoice = async order => { const response = await api.get(`/orders/${order.id}/invoice/`, { responseType:'blob' }); const url = URL.createObjectURL(response.data); const a = document.createElement('a'); a.href=url; a.download=`${order.number}.pdf`; a.click(); URL.revokeObjectURL(url) }
  if (!user) return <div className="loader page" />
  return <div className="container page"><div className="account-header"><div><span className="kicker">Your workspace</span><h1>Hello, {user.username}</h1><p>Track projects, download invoices, and use coins on your next build.</p></div><button className="button ghost" onClick={() => { logout(); navigate('/') }}><LogOut /> Sign out</button></div><div className="account-stats"><div><Coins /><span><small>Reward balance</small><strong>{user.reward_coins} coins</strong></span></div><div><Package /><span><small>Total orders</small><strong>{orders.length}</strong></span></div><div><Truck /><span><small>Active deliveries</small><strong>{orders.filter(o => !['delivered','cancelled'].includes(o.status)).length}</strong></span></div></div><section className="orders-section"><h2>Your orders</h2>{orders.length ? orders.map(order => <article className="order-card" key={order.id}><div><small>{new Date(order.created_at).toLocaleDateString('en-IN')}</small><h3>{order.number}</h3><span className={`order-status ${order.status}`}>{order.status}</span></div><div className="order-items">{order.items.slice(0,2).map(x => <span key={x.sku}>{x.product_name} × {x.quantity}</span>)}{order.items.length > 2 && <small>+{order.items.length - 2} more</small>}</div><strong>₹{Number(order.total).toLocaleString('en-IN')}</strong><button className="icon-btn invoice" onClick={() => downloadInvoice(order)} title="Download invoice"><Download /></button></article>) : <div className="empty"><Package /><h3>No orders yet</h3><p>Your completed checkout will appear here.</p><Link to="/shop" className="button primary">Explore projects</Link></div>}</section></div>
}
