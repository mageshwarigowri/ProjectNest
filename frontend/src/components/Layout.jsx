import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { Menu, Moon, ShoppingBag, Sun, UserRound, X, Zap } from 'lucide-react'
import { useStore } from '../StoreContext'
import Chatbot from './Chatbot'

export default function Layout() {
  const { cart, theme, setTheme, authenticated } = useStore()
  const [open, setOpen] = useState(false)
  const count = cart.reduce((n, x) => n + x.quantity, 0)
  return <div className="app-shell">
    <div className="announcement"><Zap size={14} /> Free shipping above ₹1,999 · Earn coins on every order</div>
    <header className="navbar container">
      <Link to="/" className="logo"><span>PN</span>ProjectNest</Link>
      <button className="icon-btn menu-btn" onClick={() => setOpen(!open)} aria-label="Toggle navigation">{open ? <X /> : <Menu />}</button>
      <nav className={open ? 'nav-links open' : 'nav-links'} onClick={() => setOpen(false)}>
        <NavLink to="/">Home</NavLink><NavLink to="/shop">Projects</NavLink><a href="/#categories">Categories</a><a href="/#why-us">Why us</a>
      </nav>
      <div className="nav-actions">
        <button className="icon-btn" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} aria-label="Toggle theme">{theme === 'light' ? <Moon /> : <Sun />}</button>
        <Link className="icon-btn" to={authenticated ? '/account' : '/login'} aria-label="Account"><UserRound /></Link>
        <Link className="icon-btn bag" to="/cart" aria-label="Cart"><ShoppingBag />{count > 0 && <b>{count}</b>}</Link>
      </div>
    </header>
    <main><Outlet /></main>
    <footer>
      <div className="container footer-grid"><div><Link to="/" className="logo light"><span>PN</span>ProjectNest</Link><p>Practical kits for curious builders. Learn by making something real.</p></div><div><h4>Explore</h4><Link to="/shop">All projects</Link><a href="/#categories">Categories</a><Link to="/account">Track order</Link></div><div><h4>Support</h4><a href="mailto:support@projectnest.local">Contact us</a><span>Shipping & returns</span><span>FAQs</span></div><div><h4>Build with us</h4><p>New project drops and practical learning tips—without the noise.</p><div className="subscribe"><input placeholder="you@example.com" /><button>Join</button></div></div></div>
      <div className="container footer-bottom"><span>© 2026 ProjectNest</span><span>Made for builders in India</span></div>
    </footer>
    <Chatbot />
  </div>
}

