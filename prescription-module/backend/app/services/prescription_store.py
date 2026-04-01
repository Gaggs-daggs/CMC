"""In-memory storage for prescriptions and analysis results."""

from app.models.schemas import (
    PrescriptionData,
    MedicineAnalysis,
    DrugInteraction,
    ReminderResponse,
)


class PrescriptionStore:
    def __init__(self):
        self._prescriptions: dict[str, PrescriptionData] = {}
        self._analyses: dict[str, list[MedicineAnalysis]] = {}
        self._interactions: dict[str, list[DrugInteraction]] = {}
        self._overall_advice: dict[str, str] = {}
        self._reminders: dict[str, list[ReminderResponse]] = {}
        self._chat_history: dict[str, list[dict]] = {}

    def save_prescription(self, data: PrescriptionData) -> None:
        self._prescriptions[data.prescription_id] = data

    def get_prescription(self, prescription_id: str) -> PrescriptionData | None:
        return self._prescriptions.get(prescription_id)

    def save_analyses(self, prescription_id: str, analyses: list[MedicineAnalysis]) -> None:
        self._analyses[prescription_id] = analyses

    def get_analyses(self, prescription_id: str) -> list[MedicineAnalysis]:
        return self._analyses.get(prescription_id, [])

    def save_interactions(self, prescription_id: str, interactions: list[DrugInteraction]) -> None:
        self._interactions[prescription_id] = interactions

    def get_interactions(self, prescription_id: str) -> list[DrugInteraction]:
        return self._interactions.get(prescription_id, [])

    def save_overall_advice(self, prescription_id: str, advice: str) -> None:
        self._overall_advice[prescription_id] = advice

    def get_overall_advice(self, prescription_id: str) -> str:
        return self._overall_advice.get(prescription_id, "")

    def add_chat_message(self, prescription_id: str, role: str, content: str) -> None:
        if prescription_id not in self._chat_history:
            self._chat_history[prescription_id] = []
        self._chat_history[prescription_id].append({"role": role, "content": content})

    def get_chat_history(self, prescription_id: str) -> list[dict]:
        return self._chat_history.get(prescription_id, [])

    def save_reminder(self, reminder: ReminderResponse) -> None:
        pid = reminder.prescription_id
        if pid not in self._reminders:
            self._reminders[pid] = []
        self._reminders[pid].append(reminder)

    def get_reminders(self, prescription_id: str) -> list[ReminderResponse]:
        return self._reminders.get(prescription_id, [])

    def list_all_prescriptions(self) -> list[PrescriptionData]:
        return list(self._prescriptions.values())


store = PrescriptionStore()
