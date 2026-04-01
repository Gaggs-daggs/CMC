export default function MedicineCard({ medicine, analysis, index, isSelected, onClick }) {
    return (
        <div
            className={`medicine-card ${isSelected ? 'selected' : ''}`}
            style={{ animationDelay: `${index * 0.1}s` }}
            onClick={onClick}
        >
            <div className="medicine-card-header">
                <span className="medicine-name">{medicine.name}</span>
                {medicine.dosage && (
                    <span className="medicine-dosage">{medicine.dosage}</span>
                )}
            </div>

            <div className="medicine-details">
                {medicine.frequency && (
                    <div className="medicine-detail">
                        <span className="medicine-detail-icon">🔄</span>
                        <span>{medicine.frequency}</span>
                    </div>
                )}
                {medicine.duration && (
                    <div className="medicine-detail">
                        <span className="medicine-detail-icon">📅</span>
                        <span>{medicine.duration}</span>
                    </div>
                )}
                {medicine.timing && (
                    <div className="medicine-detail">
                        <span className="medicine-detail-icon">⏰</span>
                        <span>{medicine.timing}</span>
                    </div>
                )}
                {medicine.instructions && (
                    <div className="medicine-detail">
                        <span className="medicine-detail-icon">📝</span>
                        <span>{medicine.instructions}</span>
                    </div>
                )}
            </div>

            {analysis?.purpose && (
                <p style={{ marginTop: 12, fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.5 }}>
                    {analysis.purpose}
                </p>
            )}
        </div>
    )
}
