import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, 
    QLabel, QTabWidget, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE = "http://localhost:8000/api"
AUTH = ("admin", "admin123")

class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Professional Onyx Dark Theme for charts
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#171717')
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#171717')
        self.axes.tick_params(colors='#94a3b8', labelsize=8)
        self.axes.xaxis.label.set_color('#94a3b8')
        self.axes.yaxis.label.set_color('#94a3b8')
        for spine in self.axes.spines.values():
            spine.set_color('#334155')
        fig.tight_layout()
        super(ChartCanvas, self).__init__(fig)

class EquipmentVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setMinimumSize(1100, 750)
        
        # Professional Onyx Theme
        self.setStyleSheet("""
            QMainWindow { background-color: #000000; }
            QWidget { color: #f8fafc; font-family: 'Segoe UI', Arial; }
            
            QTabWidget::pane { border: 1px solid #27272a; top: -1px; background: #0a0a0a; border-radius: 4px; }
            QTabBar::tab { 
                background: #18181b; 
                padding: 12px 24px; 
                margin-right: 4px; 
                border: 1px solid #27272a; 
                border-bottom: none; 
                border-top-left-radius: 4px; 
                border-top-right-radius: 4px; 
            }
            QTabBar::tab:selected { background: #000000; border-bottom: 2px solid #ffffff; }
            
            QPushButton { 
                background-color: #ffffff; 
                color: #000000;
                border-radius: 6px; 
                padding: 10px 20px; 
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
            QPushButton:disabled { background-color: #27272a; color: #52525b; }
            
            QTableWidget { 
                background-color: #0a0a0a; 
                gridline-color: #27272a;
                border: none;
                alternate-background-color: #111111;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #18181b; }
            QHeaderView::section { background-color: #171717; color: #94a3b8; padding: 12px; border: none; border-bottom: 1px solid #27272a; font-weight: bold; }
            
            /* File Dialog Fixes */
            QFileDialog { background-color: #0f172a; }
            QFileDialog QListView, QFileDialog QTreeView { background-color: #1e293b; color: #f8fafc; }
            QFileDialog QLineEdit { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 5px; }
            QFileDialog QPushButton { padding: 5px 15px; min-width: 80px; }
            QFileDialog QLabel { color: #f8fafc; }
            QFileDialog QComboBox { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; }
            
            #HeaderFrame { background-color: #0a0a0a; border-bottom: 1px solid #27272a; }
            #StatBox { background-color: #171717; border: 1px solid #27272a; border-radius: 8px; border-left: 4px solid #ffffff; }
        """)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Section
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        title_box = QVBoxLayout()
        title_label = QLabel("EQUIPMENT VISUALIZER")
        title_label.setStyleSheet("font-size: 16pt; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        sub_title = QLabel("Internal Analysis Dashboard")
        sub_title.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        title_box.addWidget(title_label)
        title_box.addWidget(sub_title)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.upload_btn = QPushButton("UPLOAD CSV")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.clicked.connect(self.upload_csv)
        header_layout.addWidget(self.upload_btn)
        
        main_layout.addWidget(header_frame)

        # Stats Cards Layout
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        main_layout.addLayout(self.stats_layout)
        
        self.create_stat_card("TOTAL UNITS", "--", "Count")
        self.create_stat_card("AVG FLOWRATE", "--", "m³/h")
        self.create_stat_card("AVG PRESSURE", "--", "bar")
        self.create_stat_card("AVG TEMP", "--", "°C")

        # Tabs Section
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Table Tab
        self.data_tab = QTableWidget()
        self.data_tab.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_tab.setShowGrid(False)
        self.data_tab.setAlternatingRowColors(True)
        self.tabs.addTab(self.data_tab, "INVENTORY LOG")

        # Chart Tab
        self.chart_tab = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_tab)
        self.canvas = ChartCanvas(self.chart_tab)
        self.chart_layout.addWidget(self.canvas)
        self.tabs.addTab(self.chart_tab, "ANALYTICS")

    def create_stat_card(self, label, value, unit):
        box = QFrame()
        box.setObjectName("StatBox")
        box.setMinimumHeight(100)
        layout = QVBoxLayout(box)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 8pt; font-weight: bold;")
        
        v_layout = QHBoxLayout()
        val = QLabel(value)
        val.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffffff;")
        unt = QLabel(unit)
        unt.setStyleSheet("font-size: 9pt; color: #52525b;")
        v_layout.addWidget(val)
        v_layout.addWidget(unt)
        v_layout.addStretch()
        
        layout.addWidget(lbl)
        layout.addLayout(v_layout)
        
        self.stats_layout.addWidget(box)
        
        # Store references to update later (using object names)
        box.setProperty("type", label)
        val.setObjectName(f"val_{label.replace(' ', '_')}")

    def upload_csv(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Equipment Data", "", "CSV Files (*.csv)", options=options)
        
        if file_path:
            self.upload_btn.setEnabled(False)
            self.upload_btn.setText("PROCESSING...")
            QApplication.processEvents() # Update UI
            
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(f"{API_BASE}/upload/", files=files, auth=AUTH)
                
                if response.status_code == 201:
                    data = response.json()
                    self.display_data(data)
                    QMessageBox.information(self, "Success", "Data processed successfully.")
                else:
                    QMessageBox.warning(self, "Error", f"Upload failed: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"System Error: {str(e)}")
            finally:
                self.upload_btn.setEnabled(True)
                self.upload_btn.setText("UPLOAD CSV")

    def display_data(self, data):
        # Update Stats Cards
        self.findChild(QLabel, "val_TOTAL_UNITS").setText(str(data['total_count']))
        self.findChild(QLabel, "val_AVG_FLOWRATE").setText(f"{data['avg_flowrate']:.1f}")
        self.findChild(QLabel, "val_AVG_PRESSURE").setText(f"{data['avg_pressure']:.1f}")
        self.findChild(QLabel, "val_AVG_TEMP").setText(f"{data['avg_temperature']:.1f}")

        # Update Table
        records = data['equipment_records']
        self.data_tab.setRowCount(len(records))
        self.data_tab.setColumnCount(5)
        self.data_tab.setHorizontalHeaderLabels(["EQUIPMENT NAME", "TYPE", "FLOWRATE", "PRESSURE", "TEMP"])
        self.data_tab.horizontalHeader().setStretchLastSection(True)

        for i, rec in enumerate(records):
            items = [rec['name'], rec['equipment_type'], str(rec['flowrate']), str(rec['pressure']), str(rec['temperature'])]
            for j, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignLeft if j < 2 else Qt.AlignRight))
                self.data_tab.setItem(i, j, item)

        # Update Charts
        dist = data['type_distribution']
        self.canvas.axes.clear()
        colors = ['#ffffff', '#a1a1aa', '#71717a', '#3f3f46', '#27272a']
        self.canvas.axes.bar(dist.keys(), dist.values(), color=colors[:len(dist)])
        self.canvas.axes.set_title("UNITS BY CATEGORY", color='#ffffff', pad=20, weight='bold')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EquipmentVisualizerApp()
    window.show()
    sys.exit(app.exec_())
