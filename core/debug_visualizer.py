from pathlib import Path
import cv2
import numpy as np
from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtCore import Qt, Signal, Slot

from ui.ui_main_window import Ui_MainWindow
from core.domain.metrics import Metrics


class DebugVisualizer(QMainWindow, Ui_MainWindow):
    source_selected = Signal(str)
    update_ready = Signal(np.ndarray, Metrics)
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.setWindowTitle("Vision Pipeline Debugger")
        self.setWindowIcon(QIcon(str(Path(__file__).parent.parent / "ui" / "assets" / "icon.png")))
        self.dataSelectPushButton.clicked.connect(self.select_data_source)
        self.update_ready.connect(self.handle_update)
        
        
    def select_data_source(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Choose a dataset folder path",
            "./data",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if not folder_path:
            return
        
        self.statusBar().showMessage(f"{folder_path} selected")
        self.source_selected.emit(folder_path)
    
    
    @Slot(np.ndarray, Metrics)
    def handle_update(self, frame: np.ndarray, metrics: Metrics):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), Qt.AspectRatioMode.KeepAspectRatio
        ))
        
        fps_text = f"FPS: {metrics.fps:.1f}"
        if metrics.iou is not None:
            iou_text = f" | IoU: {metrics.iou:.3f}"
            if metrics.iou >= 0.7:
                color = "#1FDD1F"
            elif metrics.iou >= 0.4:
                color = "#ff9800"
            else:
                color = "#f44336"
        else:
            iou_text = " | IoU: N/A"
            color = "#aaaaaa"
            
        self.metricsLabel.setText(f"{fps_text}{iou_text}")
        self.metricsLabel.setStyleSheet(f"color: {color};")