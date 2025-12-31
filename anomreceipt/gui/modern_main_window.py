"""
Modern, professional Windows GUI for AnomReceipt.
Built with PySide6/Qt for native Windows feel.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QTextEdit, QFileDialog, QProgressBar,
    QFrame, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from pathlib import Path
from typing import Optional

from ..core import get_logger, ErrorHandler, with_error_handling
from ..ocr import OCREngine
from .theme_manager import ThemeManager
from .status_widget import StatusWidget

logger = get_logger(__name__)


class OCRWorker(QThread):
    """Background worker for OCR processing."""
    
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int, str)
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.ocr_engine = OCREngine()
    
    def run(self):
        """Run OCR processing in background thread."""
        try:
            self.progress.emit(10, "Loading image...")
            logger.info(f"Processing image: {self.image_path}")
            
            self.progress.emit(30, "Preprocessing image...")
            
            self.progress.emit(50, "Performing OCR...")
            result = self.ocr_engine.process_image(self.image_path)
            
            if result:
                self.progress.emit(100, "Complete")
                self.finished.emit(result)
            else:
                self.error.emit("OCR processing failed")
        
        except Exception as e:
            logger.error(f"OCR worker error: {e}", exc_info=True)
            self.error.emit(str(e))


class ModernMainWindow(QMainWindow):
    """
    Modern, professional main window for AnomReceipt.
    Native Windows feeling with clean, modern design.
    """
    
    def __init__(self):
        super().__init__()
        
        logger.info("Initializing ModernMainWindow")
        
        # Initialize components
        self.theme_manager = ThemeManager()
        self.ocr_engine = OCREngine()
        self.current_image_path: Optional[str] = None
        self.ocr_worker: Optional[OCRWorker] = None
        
        # Setup UI
        self.setup_window()
        self.setup_ui()
        self.apply_theme()
        
        logger.info("ModernMainWindow initialized successfully")
    
    def setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("AnomReceipt - Professional Receipt OCR")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center window on screen
        screen = self.screen().geometry()
        window_rect = self.geometry()
        x = (screen.width() - window_rect.width()) // 2
        y = (screen.height() - window_rect.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area with splitter
        splitter = self.create_content_area()
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
    
    def create_header(self) -> QWidget:
        """Create header with title and controls."""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Title
        title_label = QLabel("AnomReceipt")
        title_label.setObjectName("title")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Theme toggle
        theme_btn = QPushButton("🌓 Theme")
        theme_btn.setObjectName("themeButton")
        theme_btn.setFixedSize(100, 40)
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)
        
        return header
    
    def create_content_area(self) -> QSplitter:
        """Create main content area with image and text panels."""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Left panel - Image preview
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Text output
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes (50-50 split)
        splitter.setSizes([600, 600])
        
        return splitter
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with image preview and controls."""
        panel = QFrame()
        panel.setObjectName("panel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Receipt Image")
        title.setObjectName("sectionTitle")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Image preview area
        preview_container = QFrame()
        preview_container.setObjectName("imagePreview")
        preview_container.setMinimumHeight(400)
        
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: #f0f0f0; border-radius: 8px;")
        self.image_label.setText("No image loaded\n\nClick 'Load Image' to begin")
        preview_layout.addWidget(self.image_label)
        
        layout.addWidget(preview_container, 1)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("📁 Load Image")
        self.load_btn.setObjectName("primaryButton")
        self.load_btn.setFixedHeight(45)
        self.load_btn.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_btn)
        
        self.process_btn = QPushButton("🔍 Process OCR")
        self.process_btn.setObjectName("primaryButton")
        self.process_btn.setFixedHeight(45)
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_ocr)
        button_layout.addWidget(self.process_btn)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with structured text output."""
        panel = QFrame()
        panel.setObjectName("panel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Extracted Text")
        title.setObjectName("sectionTitle")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Text output area
        self.text_output = QTextEdit()
        self.text_output.setObjectName("textOutput")
        self.text_output.setReadOnly(False)
        self.text_output.setPlaceholderText(
            "Extracted text will appear here...\n\n"
            "You can edit the text after OCR processing."
        )
        text_font = QFont("Courier New", 10)
        self.text_output.setFont(text_font)
        layout.addWidget(self.text_output, 1)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_btn = QPushButton("💾 Save Text")
        self.save_btn.setObjectName("secondaryButton")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_text)
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_btn)
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setObjectName("secondaryButton")
        self.copy_btn.setFixedHeight(40)
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def create_status_bar(self) -> QWidget:
        """Create status bar at bottom."""
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(40)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(20, 5, 20, 5)
        
        # Status widget
        self.status_widget = StatusWidget()
        layout.addWidget(self.status_widget)
        
        layout.addStretch()
        
        # Version label
        version_label = QLabel("v2.0.0")
        version_label.setObjectName("versionLabel")
        layout.addWidget(version_label)
        
        return status_bar
    
    @with_error_handling(
        error_title="Failed to Load Image",
        error_message="Could not load the selected image file"
    )
    def load_image(self):
        """Load an image file."""
        logger.info("Opening file dialog...")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Receipt Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        
        if not file_path:
            logger.info("File dialog cancelled")
            return
        
        logger.info(f"Loading image: {file_path}")
        self.current_image_path = file_path
        
        # Load and display image
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            ErrorHandler.show_error(
                "Invalid Image",
                "The selected file is not a valid image.",
                parent=self
            )
            return
        
        # Scale image to fit preview (ensure reasonable display size)
        preview_size = self.image_label.size()
        
        # Use actual preview size, but ensure minimum reasonable size
        # to avoid tiny displays on first load
        if preview_size.width() < 100 or preview_size.height() < 100:
            # On first load, use a reasonable default
            target_width = 600
            target_height = 600
        else:
            # Use actual preview area size
            target_width = preview_size.width()
            target_height = preview_size.height()
        
        scaled_pixmap = pixmap.scaled(
            target_width,
            target_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # Enable process button
        self.process_btn.setEnabled(True)
        self.status_widget.show_info(f"Image loaded: {Path(file_path).name}")
        
        logger.info("Image loaded successfully")
    
    @with_error_handling(
        error_title="OCR Processing Failed",
        error_message="Failed to process the receipt image"
    )
    def process_ocr(self):
        """Process current image with OCR."""
        if not self.current_image_path:
            return
        
        logger.info("Starting OCR processing...")
        
        # Disable buttons during processing
        self.process_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.status_widget.show_processing("Processing image with OCR...")
        
        # Create and start worker thread
        self.ocr_worker = OCRWorker(self.current_image_path)
        self.ocr_worker.finished.connect(self.on_ocr_complete)
        self.ocr_worker.error.connect(self.on_ocr_error)
        self.ocr_worker.progress.connect(self.on_ocr_progress)
        self.ocr_worker.start()
    
    def on_ocr_progress(self, value: int, message: str):
        """Handle OCR progress updates."""
        self.progress_bar.setValue(value)
        self.status_widget.show_processing(message)
    
    def on_ocr_complete(self, result):
        """Handle OCR completion."""
        logger.info("OCR processing completed")
        
        # Re-enable buttons
        self.process_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Display result
        if result and result.structured_text:
            self.text_output.setPlainText(result.structured_text)
            self.status_widget.show_success(
                f"OCR complete (Confidence: {result.confidence:.1f}%)"
            )
            
            # Enable action buttons
            self.save_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
            self.copy_btn.setEnabled(True)
        else:
            ErrorHandler.show_warning(
                "No Text Found",
                "OCR did not extract any text from the image.",
                parent=self
            )
            self.status_widget.show_warning("No text extracted")
    
    def on_ocr_error(self, error_msg: str):
        """Handle OCR error."""
        logger.error(f"OCR error: {error_msg}")
        
        # Re-enable buttons
        self.process_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.status_widget.show_error(f"OCR failed: {error_msg}")
        
        ErrorHandler.show_error(
            "OCR Processing Failed",
            f"Failed to process the image.\n\n{error_msg}",
            parent=self
        )
    
    @with_error_handling(
        error_title="Failed to Save Text",
        error_message="Could not save the text to file"
    )
    def save_text(self):
        """Save extracted text to file."""
        text = self.text_output.toPlainText()
        if not text:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Extracted Text",
            "receipt_text.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not file_path:
            return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        self.status_widget.show_success(f"Text saved: {Path(file_path).name}")
        logger.info(f"Text saved to: {file_path}")
    
    def clear_text(self):
        """Clear text output."""
        self.text_output.clear()
        self.save_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.status_widget.show_info("Text cleared")
    
    def copy_text(self):
        """Copy text to clipboard."""
        text = self.text_output.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_widget.show_success("Text copied to clipboard")
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme_manager.toggle_theme()
        self.apply_theme()
        
        theme_name = "Dark" if self.theme_manager.is_dark_theme() else "Light"
        self.status_widget.show_info(f"Switched to {theme_name} theme")
        logger.info(f"Theme changed to: {theme_name}")
    
    def apply_theme(self):
        """Apply current theme to the application."""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
        logger.debug("Theme applied")
