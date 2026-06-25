from typing import Any, Dict
from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class WalletEngine:
    """
    PRO-Version des WalletManagers:
    - Verwaltet Wallet-Adressen, Guthaben (ETH) und digitale Assets (NFTs)
    - Nutzt das transaktionssichere SQLite-Langzeitgedächtnis statt lokaler JSONs
    - Vollständig integriert in das Engine-Manager-Ökosystem
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("WalletEngine benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")

    def _get_wallet_data(self) -> Dict[str, Any]:
        """Lädt den aktuellen Wallet-Zustand sicher aus der SQLite-Datenbank."""
        return self.state.get_state(
            "wallet", 
            {"adresse": "Keine gesetzt", "balance": "0 ETH", "assets": []}
        )

    def set_address(self, address: str) -> str:
        """Aktualisiert die Wallet-Adresse im verschlüsselten/gesicherten DB-State."""
        wallet = self._get_wallet_data()
        wallet["adresse"] = address
        
        self.state.set_state("wallet", wallet)
        log_doctor(f"WalletEngine: Adresse erfolgreich auf '{address}' aktualisiert.")
        return f"Wallet-Adresse wurde auf {address} aktualisiert."

    def update_balance(self, balance_str: str) -> str:
        """Aktualisiert das ausgelesene Krypto-Guthaben (z.B. via API-Scout)."""
        wallet = self._get_wallet_data()
        wallet["balance"] = balance_str
        
        self.state.set_state("wallet", wallet)
        log_doctor(f"WalletEngine: Guthaben aktualisiert -> {balance_str}")
        return f"Guthaben auf {balance_str} gesetzt."

    def get_status(self) -> str:
        """Gibt den aktuellen Status formatiert zurück (perfekt für das GUI-Log)."""
        wallet = self._get_wallet_data()
        return f"Adresse: {wallet['adresse']} | Guthaben: {wallet['balance']} | Assets: {len(wallet['assets'])}"


# Abwärtskompatibler Wrapper (falls alte Module die Funktion direkt importieren)
def wallet_manager_legacy(befehl: str, wert: str, engine_manager: EngineManager) -> str:
    """Erlaubt alten Modulen den Zugriff über die neue WalletEngine-Struktur."""
    engine = WalletEngine(engine_manager)
    if befehl == "set_adresse":
        return engine.set_address(wert)
    elif befehl == "status":
        return engine.get_status()
    return "Befehl unbekannt."