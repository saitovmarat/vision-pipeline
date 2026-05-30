from pathlib import Path
import cv2
import numpy as np
import time
from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtCore import Qt, Signal, Slot

from ui.ui_main_window import Ui_MainWindow
from core.domain.metrics import Metrics


class DebugVisualizer(QMainWindow, Ui_MainWindow):
    source_selected = Signal(str)
    update_ready = Signal(np.ndarray, Metrics, float, float)
    
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
    
    
    @Slot(np.ndarray, Metrics, float, float)
    def handle_update(self, frame: np.ndarray, metrics: Metrics, filter_time: float, pred_time: float):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        
        if metrics is None:
            pred_fps_text = "Pred FPS: --"
            filter_fps_text = " | Filter FPS: --"
            map50_text = " | mAP@0.5: --"
            map50_95_text = " | mAP@[0.5:0.95]: --"
            color = "#aaaaaa"
        else:
            pred_fps_text = f"Pred FPS: {(1.0 / pred_time):.0f}"
            filter_fps_text = f" | Filter FPS: {(1.0 / filter_time):.0f}"
            if metrics.mAP50 is not None and metrics.mAP50_95 is not None:
                map50_text = f" | mAP@0.5: {metrics.mAP50:.3f}"
                map50_95_text = f" | mAP@[0.5:0.95]: {metrics.mAP50_95:.3f}"
                if metrics.mAP50 >= 0.7:
                    color = "#1FDD1F"
                elif metrics.mAP50 >= 0.4:
                    color = "#ff9800"
                else:
                    color = "#f44336"
            else:
                map50_text = " | mAP@0.5: --"
                map50_95_text = " | mAP@[0.5:0.95]: --"
                color = "#aaaaaa"
            
        self.metricsLabel.setText(f"{pred_fps_text}{filter_fps_text}{map50_text}{map50_95_text}")
        self.metricsLabel.setStyleSheet(f"color: {color};")