import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Shop from './pages/Shop'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Login from './pages/Login'
import Account from './pages/Account'
import { Faqs, ShippingReturns } from './pages/Support'

export default function App() {
  return <Routes><Route element={<Layout />}><Route index element={<Home />} /><Route path="shop" element={<Shop />} /><Route path="products/:slug" element={<ProductDetail />} /><Route path="cart" element={<Cart />} /><Route path="login" element={<Login />} /><Route path="account" element={<Account />} /><Route path="shipping-returns" element={<ShippingReturns />} /><Route path="faqs" element={<Faqs />} /><Route path="*" element={<Shop />} /></Route></Routes>
}
