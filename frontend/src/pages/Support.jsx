import { Link } from 'react-router-dom'

export function ShippingReturns() {
  return <div className="container page support-page">
    <span className="kicker">Customer support</span>
    <h1>Shipping & returns</h1>
    <section><h2>Shipping</h2><p>Shipping is ₹99 and free for orders of ₹1,999 or more. In-stock orders are normally dispatched within 1–2 business days. Tracking details appear in your account after dispatch.</p></section>
    <section><h2>Returns</h2><p>Unused items may be requested for return within seven days of delivery. Please report damaged or incomplete kits within 48 hours and include your order number.</p></section>
    <Link to="/shop" className="button primary">Continue shopping</Link>
  </div>
}

export function Faqs() {
  const questions = [
    ['Are taxes included?', 'Yes. All displayed product prices include applicable tax.'],
    ['Which payment methods are available?', 'Cash on delivery is available. Razorpay checkout can be enabled when production payment keys are configured.'],
    ['How do reward coins work?', 'Delivered orders earn one coin per ₹100 spent. One coin redeems for ₹1, up to 20% of a future order.'],
    ['Where can I track an order?', 'Sign in and open Account to see order status, shipment updates, and invoices.'],
  ]
  return <div className="container page support-page">
    <span className="kicker">Helpful answers</span>
    <h1>Frequently asked questions</h1>
    <div className="faq-list">{questions.map(([question, answer]) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}</div>
    <Link to="/shop" className="button primary">Explore projects</Link>
  </div>
}
