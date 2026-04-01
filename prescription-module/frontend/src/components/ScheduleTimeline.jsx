export default function ScheduleTimeline({ medicines }) {
    if (!medicines || medicines.length === 0) return null

    const parseTimings = (med) => {
        const timings = []
        const freq = (med.frequency || '').toLowerCase()
        const timing = (med.timing || '').toLowerCase()

        if (freq.includes('once') || freq.includes('1')) {
            timings.push(timing.includes('night') || timing.includes('evening') ? '🌙 Night' : '🌅 Morning')
        } else if (freq.includes('twice') || freq.includes('2')) {
            timings.push('🌅 Morning', '🌙 Night')
        } else if (freq.includes('thrice') || freq.includes('three') || freq.includes('3')) {
            timings.push('🌅 Morning', '☀️ Afternoon', '🌙 Night')
        } else if (freq.includes('four') || freq.includes('4')) {
            timings.push('🌅 Morning', '☀️ Noon', '🌇 Evening', '🌙 Night')
        } else {
            timings.push('💊 As prescribed')
        }

        return timings
    }

    return (
        <div className="schedule-section">
            <h3>📅 Medication Schedule</h3>

            <div className="schedule-grid">
                {medicines.map((med, i) => {
                    const timings = parseTimings(med)
                    return (
                        <div key={i} className="schedule-card fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
                            <div className="schedule-med-name">{med.name}</div>
                            <div className="schedule-info">
                                {med.dosage && <span>{med.dosage}</span>}
                                {med.dosage && med.duration && <span> • </span>}
                                {med.duration && <span>{med.duration}</span>}
                            </div>
                            {med.instructions && (
                                <div className="schedule-info" style={{ fontStyle: 'italic', color: 'var(--text-dim)' }}>
                                    {med.instructions}
                                </div>
                            )}
                            <div className="schedule-timing">
                                {timings.map((t, j) => (
                                    <span key={j} className="timing-badge">{t}</span>
                                ))}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
