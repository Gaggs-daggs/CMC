export default function AnalysisPanel({ analysis }) {
    if (!analysis) {
        return (
            <div className="analysis-panel">
                <div className="empty-state">
                    <div className="empty-state-icon">👈</div>
                    <p>Select a medicine to see detailed analysis</p>
                </div>
            </div>
        )
    }

    return (
        <div className="analysis-panel">
            <h3>💊 {analysis.medicine_name}</h3>

            {analysis.purpose && (
                <div className="analysis-section">
                    <div className="analysis-section-title">Purpose</div>
                    <p>{analysis.purpose}</p>
                </div>
            )}

            {analysis.how_it_works && (
                <div className="analysis-section">
                    <div className="analysis-section-title">How It Works</div>
                    <p>{analysis.how_it_works}</p>
                </div>
            )}

            {analysis.benefits?.length > 0 && (
                <div className="analysis-section">
                    <div className="analysis-section-title">✅ Benefits</div>
                    <div className="analysis-tags">
                        {analysis.benefits.map((b, i) => (
                            <span key={i} className="tag tag-success">{b}</span>
                        ))}
                    </div>
                </div>
            )}

            {analysis.common_side_effects?.length > 0 && (
                <div className="analysis-section">
                    <div className="analysis-section-title">⚠️ Common Side Effects</div>
                    <div className="analysis-tags">
                        {analysis.common_side_effects.map((s, i) => (
                            <span key={i} className="tag tag-warning">{s}</span>
                        ))}
                    </div>
                </div>
            )}

            {analysis.serious_side_effects?.length > 0 && (
                <div className="analysis-section">
                    <div className="analysis-section-title">🚨 Serious Side Effects</div>
                    <div className="analysis-tags">
                        {analysis.serious_side_effects.map((s, i) => (
                            <span key={i} className="tag tag-danger">{s}</span>
                        ))}
                    </div>
                </div>
            )}

            {analysis.precautions?.length > 0 && (
                <div className="analysis-section">
                    <div className="analysis-section-title">⚡ Precautions</div>
                    <div className="analysis-tags">
                        {analysis.precautions.map((p, i) => (
                            <span key={i} className="tag tag-info">{p}</span>
                        ))}
                    </div>
                </div>
            )}

            {analysis.food_interactions && (
                <div className="analysis-section">
                    <div className="analysis-section-title">🍽️ Food Interactions</div>
                    <p>{analysis.food_interactions}</p>
                </div>
            )}

            {analysis.contraindications?.length > 0 && (
                <div className="analysis-section">
                    <div className="analysis-section-title">🚫 Contraindications</div>
                    <div className="analysis-tags">
                        {analysis.contraindications.map((c, i) => (
                            <span key={i} className="tag tag-danger">{c}</span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
