import { createContext, useContext, useEffect, useState } from 'react'
import api from './api'

const StoreContext = createContext(null)
export function StoreProvider({ children }) {
  const [user, setUser] = useState(null)
  const [cart, setCart] = useState(() => JSON.parse(localStorage.getItem('guest_cart') || '[]'))
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')
  const [toast, setToast] = useState(null)
  const authenticated = Boolean(localStorage.getItem('access_token'))

  useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem('theme', theme) }, [theme])
  useEffect(() => { if (authenticated) { api.get('/auth/me/').then(r => setUser(r.data)).catch(() => setUser(null)); api.get('/cart/').then(r => setCart(r.data.items)).catch(() => {}) } }, [authenticated])
  useEffect(() => { if (!authenticated) localStorage.setItem('guest_cart', JSON.stringify(cart)) }, [cart, authenticated])
  const announce = (message, type = 'success') => {
    const id = Date.now()
    setToast({ id, message, type })
    window.setTimeout(() => setToast(current => current?.id === id ? null : current), 3500)
  }

  const addToCart = async (product, quantity = 1) => {
    if (product.stock_label === 'Out of stock') return announce('This kit is currently out of stock')
    try {
      if (authenticated) { const { data } = await api.post('/cart/', { product_id: product.id, quantity }); setCart(data.items) }
      else setCart(items => { const found = items.find(x => x.product.id === product.id); return found ? items.map(x => x.product.id === product.id ? { ...x, quantity: x.quantity + quantity } : x) : [...items, { id: `guest-${product.id}`, product, quantity, total: product.sale_price }] })
      announce(`${product.name} added to cart`)
    } catch (error) {
      announce(error.response?.data?.detail || 'Could not add this item to the cart.', 'error')
    }
  }
  const updateCart = async (productId, quantity) => {
    if (authenticated) { const { data } = await api.patch('/cart/', { product_id: productId, quantity }); setCart(data.items) }
    else setCart(items => quantity <= 0 ? items.filter(x => x.product.id !== productId) : items.map(x => x.product.id === productId ? { ...x, quantity } : x))
  }
  const removeFromCart = async (productId) => {
    if (authenticated) { const { data } = await api.delete('/cart/', { data: { product_id: productId } }); setCart(data.items) }
    else setCart(items => items.filter(x => x.product.id !== productId))
  }
  const login = async (username, password) => {
    const { data } = await api.post('/auth/token/', { username, password }); localStorage.setItem('access_token', data.access); localStorage.setItem('refresh_token', data.refresh)
    const me = await api.get('/auth/me/'); setUser(me.data); const serverCart = await api.get('/cart/'); setCart(serverCart.data.items)
  }
  const logout = () => { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); setUser(null); setCart([]) }
  const value = { user, authenticated, cart, setCart, theme, setTheme, addToCart, updateCart, removeFromCart, login, logout, announce }
  return <StoreContext.Provider value={value}>{children}{toast && <div className={`toast ${toast.type}`} role="status" aria-live="polite"><b>{toast.type === 'success' ? '✓' : '!'}</b>{toast.message}</div>}</StoreContext.Provider>
}
export const useStore = () => useContext(StoreContext)
