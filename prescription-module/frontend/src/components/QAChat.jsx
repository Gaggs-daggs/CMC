import { useState, useRef, useEffect } from 'react'

export default function QAChat({ prescriptionId }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async () => {
        const question = input.trim()
        if (!question || loading) return

        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: question }])
        setLoading(true)

        try {
            const res = await fetch(`/api/v1/prescription/${prescriptionId}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question }),
            })

            if (!res.ok) throw new Error('Failed to get answer')

            const data = await res.json()
            setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I couldn\'t process your question. Please try again.',
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    const suggestions = [
        'Can I take these medicines with food?',
        'What should I avoid while taking these?',
        'Are there any serious side effects I should watch for?',
        'Can I stop taking these early if I feel better?',
    ]

    return (
        <div className="qa-section">
            <h3>💬 Ask About Your Prescription</h3>

            <div className="chat-container">
                <div className="chat-messages">
                    {messages.length === 0 && (
                        <div className="empty-state" style={{ padding: '24px 0' }}>
                            <div className="empty-state-icon">🤖</div>
                            <p style={{ marginBottom: 16 }}>Ask me anything about your medicines</p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                                {suggestions.map((s, i) => (
                                    <button
                                        key={i}
                                        className="btn-secondary"
                                        style={{ fontSize: 12, padding: '6px 12px' }}
                                        onClick={() => { setInput(s); }}
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div key={i} className={`chat-message ${msg.role}`}>
                            <div className="chat-avatar">
                                {msg.role === 'user' ? '👤' : '🤖'}
                            </div>
                            <div className="chat-bubble">{msg.content}</div>
                        </div>
                    ))}

                    {loading && (
                        <div className="chat-message assistant">
                            <div className="chat-avatar">🤖</div>
                            <div className="chat-bubble" style={{ color: 'var(--text-dim)' }}>
                                Thinking...
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    <input
                        className="chat-input"
                        type="text"
                        placeholder="Ask about side effects, dosage, interactions..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                    />
                    <button
                        className="chat-send-btn"
                        onClick={sendMessage}
                        disabled={!input.trim() || loading}
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    )
}
