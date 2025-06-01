__version__ = "0u.1.0"
import sys
from PySide6.QtCore import Qt, QLocale

from PySide6.QtWidgets import (
                             QApplication,
                             QWidget,
                             QLabel,
                             QLineEdit,
                             QVBoxLayout,
                             QComboBox,
                             QMainWindow,
                             QDialog,
                             QFormLayout,
                             QPushButton,
                             QDialogButtonBox)

from PySide6.QtGui import (
    QIntValidator,
    QFont,
    QPalette,
    QColor, QDoubleValidator)

from config_manager import ConfigManager

class PrijsAanpassenDialog(QDialog):
    def __init__(self, prijzen: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("prijzen per vel")
        self.prijzen = prijzen.copy()  # Maak een kopie van de prijzen
        
        layout = QFormLayout(self)
        
        # Dictionary om alle spinboxes bij te houden
        self.prijsvelden = {}

        # Maak voor elke papiersoort een spinbox
        for papiersoort, prijs in prijzen.items():
            prijsveld = QLineEdit()
            prijsveld.setLocale(QLocale('C'))
            # Stel een validator in die 4 decimalen toestaat
            validator = QDoubleValidator(0.0000, 100.0000, 4)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            prijsveld.setValidator(validator)
            # Zet de huidige prijs met exacte precisie
            try:
                # Gebruik format string direct met float
                prijsveld.setText(f"{float(prijs):.4f}")
            except (ValueError, TypeError):
                # Fallback waarde als er een probleem is met de conversie
                prijsveld.setText("0.0000")

            self.prijsvelden[papiersoort] = prijsveld
            layout.addRow(papiersoort, prijsveld)

        # Voeg OK en Cancel knoppen toe
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addRow(buttonBox)

    def get_nieuwe_prijzen(self) -> dict:
        nieuwe_prijzen: dict = {}
        for papiersoort, prijsveld in self.prijsvelden.items():
            # Haal het euroteken en spaties weg en converteer naar float
            prijs_tekst = prijsveld.text().replace('€', '').strip()
            try:
                nieuwe_prijzen[papiersoort] = float(prijs_tekst)
            except ValueError:
                nieuwe_prijzen[papiersoort] = 0.0
        return nieuwe_prijzen


font = QFont()
font.setPointSize(12)

label_style = """
    QLabel {
        color: #3c0c9f;
        font-weight: regular;
        font-family: Arial;
        font-size: 14px;
        padding: 5px;
    }"""

input_style = """
QlineEdit:Focus{
border: 2px solid #efb9ad;
        background-color: #b1e4d5;
}"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.papier_prijzen = self.config_manager.load_prijzen()
        self.setWindowTitle("papier calculator")
        self.setMinimumSize(280, 260)
        self.setMaximumSize(500, 500)

        #maak een centrale widget en layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 30, 10, 10)

        #maak een invoerveld voor papierhoeveelheid
        self.label = QLabel()
        self.label.setFont(font)
        self.label.setStyleSheet(label_style)
        self.number = QLineEdit()
        self.number.setFixedWidth(220)
        self.number.setFixedHeight(24)
        self.number.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.number.setPlaceholderText("voer het aantal vellen in")
        self.number.returnPressed.connect(lambda : self.papierkosten.setFocus())
        self.number.setValidator(QIntValidator(0, 100000))
        self.number.setStyleSheet(input_style)
        self.number.textChanged.connect(self.bereken)

        #maak papierkeuze met QcomboBox
        self.label2 = QLabel("kies papiersoort")
        self.label2.setFont(font)
        self.label2.setStyleSheet(label_style)
        self.papierkosten = QComboBox()
        self.papierkosten.setFixedWidth(220)
        self.papierkosten.setFixedHeight(24)
        self.papierkosten.addItems(list(self.papier_prijzen.keys()))
        self.papierkosten.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.papierkosten.installEventFilter(self)
        self.setStyleSheet(input_style)
        self.papierkosten.currentTextChanged.connect(self.bereken)

        #resultaat berekening kosten
        self.resultaat_berekening = QLabel()
        self.resultaat_berekening.setFont(font)
        self.resultaat_berekening.setStyleSheet(label_style)
        
        # Voeg een knop toe voor het aanpassen van prijzen
        self.prijzen_aanpassen_knop = QPushButton("prijs per vel (64x46) aanpassen")
        self.prijzen_aanpassen_knop.clicked.connect(self.toon_prijzen_dialog)
        layout.addWidget(self.prijzen_aanpassen_knop)

        #voeg widgets toe aan de layout
        layout.addWidget(self.label)
        layout.addWidget(self.number)
        layout.addWidget(self.label2)
        layout.addWidget(self.papierkosten)
        layout.addWidget(self.resultaat_berekening)

        #bereken het resultaat van de invoer
    def bereken(self)->None:
        try:
            #controleren of het veld leeg is
            if not self.number.text():
                self.resultaat_berekening.setText("geen goede invoer")
                return

            aantal: int = int(self.number.text())
            geselecteerd_papier: str = self.papierkosten.currentText()
            prijs_per_vel = self.papier_prijzen[geselecteerd_papier]

            totaal_prijs: float = aantal * prijs_per_vel

            self.resultaat_berekening.setText(f"papier kosten: € {totaal_prijs:.2f}")
        except ValueError:
            self.resultaat_berekening.setText("geen goede invoer")


    def toon_prijzen_dialog(self)->None:
        dialog = PrijsAanpassenDialog(self.papier_prijzen, self)
        if dialog.exec() == QDialog.Accepted:
            self.papier_prijzen = dialog.get_nieuwe_prijzen()
            # Sla de nieuwe prijzen op
            self.config_manager.save_prijzen(self.papier_prijzen)
            self.bereken()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setPalette(QPalette(QColor("#fce3c3")))
    app.setStyleSheet("QMainWindow{background-color: #d09246;}")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())