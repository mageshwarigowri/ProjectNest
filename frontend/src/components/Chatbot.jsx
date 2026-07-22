import { useEffect, useRef, useState } from 'react'
import { Bot, ExternalLink, MessageCircle, Send, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '../api'

const getSession = () => { let id = sessionStorage.getItem('chat_session'); if (!id) { id = crypto.randomUUID(); sessionStorage.setItem('chat_session', id) } return id }
export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState([{ role: 'bot', text: 'Hi! I’m the ProjectNest guide. Ask me about project kits, prices, stock, discounts, shipping, or rewards.' }])
  const end = useRef(null)
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])
  const send = async (event) => {
    event.preventDefault(); const text = message.trim(); if (!text || sending) return
    setMessages(m => [...m, { role: 'user', text }]); setMessage(''); setSending(true)
    try { const { data } = await api.post('/chat/', { message: text, session_id: getSession() }); setMessages(m => [...m, { role: 'bot', text: data.answer, links: data.links }]) }
    catch { setMessages(m => [...m, { role: 'bot', text: 'I’m having trouble connecting right now. Please try again shortly.' }]) }
    finally { setSending(false) }
  }
  return <><button className="chat-fab" onClick={() => setOpen(!open)} aria-label="Open project assistant">{open ? <X /> : <MessageCircle />}<span>Ask ProjectNest</span></button>
    {open && <section className="chat-panel" aria-label="ProjectNest assistant"><header><span><Bot /> <b>ProjectNest Guide</b></span><button onClick={() => setOpen(false)}><X /></button><small><i /> Online · Store topics only</small></header><div className="messages">{messages.map((m, i) => <div key={i} className={`message ${m.role}`}><p>{m.text}</p>{m.links?.map(link => <Link key={link.url} to={link.url} onClick={() => setOpen(false)}>{link.label}<ExternalLink size={12} /></Link>)}</div>)}{sending && <div className="message bot typing"><i /><i /><i /></div>}<div ref={end} /></div><form onSubmit={send}><input value={message} onChange={e => setMessage(e.target.value)} maxLength={500} placeholder="Ask about products or stock…" aria-label="Message" /><button disabled={!message.trim() || sending}><Send /></button></form><footer>AI can make mistakes. Verify important details.</footer></section>}
  </>
}
