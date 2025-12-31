"""
Professional theme system for AnomReceipt.
Provides modern dark and light themes with consistent styling.
"""

from typing import Dict


class ThemeManager:
    """
    Manages application themes (dark/light).
    Provides professional color schemes and styling.
    """
    
    def __init__(self):
        """Initialize theme manager with light theme."""
        self._current_theme = "light"
        
        # Define color palettes
        self.themes: Dict[str, Dict[str, str]] = {
            "light": {
                # Background colors
                "bg_primary": "#ffffff",
                "bg_secondary": "#f5f5f5",
                "bg_tertiary": "#e0e0e0",
                "bg_header": "#2c3e50",
                
                # Text colors
                "text_primary": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "text_light": "#ffffff",
                
                # Accent colors
                "accent_primary": "#3498db",
                "accent_success": "#27ae60",
                "accent_warning": "#f39c12",
                "accent_error": "#e74c3c",
                "accent_info": "#3498db",
                
                # Border colors
                "border_light": "#bdc3c7",
                "border_medium": "#95a5a6",
                "border_dark": "#7f8c8d",
                
                # Button colors
                "btn_primary_bg": "#3498db",
                "btn_primary_hover": "#2980b9",
                "btn_primary_text": "#ffffff",
                "btn_secondary_bg": "#ecf0f1",
                "btn_secondary_hover": "#bdc3c7",
                "btn_secondary_text": "#2c3e50",
            },
            "dark": {
                # Background colors
                "bg_primary": "#1e1e1e",
                "bg_secondary": "#252526",
                "bg_tertiary": "#2d2d30",
                "bg_header": "#1e1e1e",
                
                # Text colors
                "text_primary": "#e0e0e0",
                "text_secondary": "#a0a0a0",
                "text_light": "#ffffff",
                
                # Accent colors
                "accent_primary": "#3498db",
                "accent_success": "#27ae60",
                "accent_warning": "#f39c12",
                "accent_error": "#e74c3c",
                "accent_info": "#3498db",
                
                # Border colors
                "border_light": "#3e3e42",
                "border_medium": "#505050",
                "border_dark": "#6e6e6e",
                
                # Button colors
                "btn_primary_bg": "#3498db",
                "btn_primary_hover": "#2980b9",
                "btn_primary_text": "#ffffff",
                "btn_secondary_bg": "#3e3e42",
                "btn_secondary_hover": "#505050",
                "btn_secondary_text": "#e0e0e0",
            }
        }
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self._current_theme = "dark" if self._current_theme == "light" else "light"
    
    def is_dark_theme(self) -> bool:
        """Check if current theme is dark."""
        return self._current_theme == "dark"
    
    def get_color(self, key: str) -> str:
        """
        Get color value for current theme.
        
        Args:
            key: Color key (e.g., 'bg_primary')
        
        Returns:
            Color hex value
        """
        return self.themes[self._current_theme].get(key, "#000000")
    
    def get_stylesheet(self) -> str:
        """
        Generate complete stylesheet for current theme.
        
        Returns:
            CSS stylesheet string
        """
        theme = self.themes[self._current_theme]
        
        return f"""
        /* Global Styles */
        QMainWindow {{
            background-color: {theme['bg_primary']};
        }}
        
        QWidget {{
            color: {theme['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
        }}
        
        /* Header */
        QFrame#header {{
            background-color: {theme['bg_header']};
            border-bottom: 2px solid {theme['accent_primary']};
        }}
        
        QLabel#title {{
            color: {theme['text_light']};
        }}
        
        /* Panels */
        QFrame#panel {{
            background-color: {theme['bg_primary']};
            border: 1px solid {theme['border_light']};
            border-radius: 8px;
            padding: 10px;
        }}
        
        QLabel#sectionTitle {{
            color: {theme['text_primary']};
            font-weight: bold;
            font-size: 14pt;
            padding-bottom: 5px;
        }}
        
        /* Image Preview */
        QFrame#imagePreview {{
            background-color: {theme['bg_secondary']};
            border: 2px dashed {theme['border_medium']};
            border-radius: 8px;
        }}
        
        /* Text Output */
        QTextEdit#textOutput {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border_light']};
            border-radius: 4px;
            padding: 10px;
            font-family: 'Courier New', monospace;
        }}
        
        QTextEdit#textOutput:focus {{
            border: 2px solid {theme['accent_primary']};
        }}
        
        /* Primary Buttons */
        QPushButton#primaryButton {{
            background-color: {theme['btn_primary_bg']};
            color: {theme['btn_primary_text']};
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12pt;
        }}
        
        QPushButton#primaryButton:hover {{
            background-color: {theme['btn_primary_hover']};
        }}
        
        QPushButton#primaryButton:pressed {{
            background-color: {theme['btn_primary_hover']};
            padding-top: 12px;
            padding-bottom: 8px;
        }}
        
        QPushButton#primaryButton:disabled {{
            background-color: {theme['border_medium']};
            color: {theme['text_secondary']};
        }}
        
        /* Secondary Buttons */
        QPushButton#secondaryButton {{
            background-color: {theme['btn_secondary_bg']};
            color: {theme['btn_secondary_text']};
            border: 1px solid {theme['border_light']};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 10pt;
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {theme['btn_secondary_hover']};
            border-color: {theme['border_medium']};
        }}
        
        QPushButton#secondaryButton:pressed {{
            background-color: {theme['btn_secondary_hover']};
            padding-top: 10px;
            padding-bottom: 6px;
        }}
        
        QPushButton#secondaryButton:disabled {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_secondary']};
            border-color: {theme['border_light']};
        }}
        
        /* Theme Button */
        QPushButton#themeButton {{
            background-color: {theme['btn_secondary_bg']};
            color: {theme['btn_secondary_text']};
            border: 1px solid {theme['border_light']};
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 11pt;
        }}
        
        QPushButton#themeButton:hover {{
            background-color: {theme['btn_secondary_hover']};
        }}
        
        /* Progress Bar */
        QProgressBar#progressBar {{
            background-color: {theme['bg_secondary']};
            border: none;
            border-radius: 3px;
            text-align: center;
        }}
        
        QProgressBar#progressBar::chunk {{
            background-color: {theme['accent_primary']};
            border-radius: 3px;
        }}
        
        /* Status Bar */
        QFrame#statusBar {{
            background-color: {theme['bg_secondary']};
            border-top: 1px solid {theme['border_light']};
        }}
        
        QLabel#versionLabel {{
            color: {theme['text_secondary']};
            font-size: 9pt;
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {theme['border_light']};
            width: 2px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {theme['accent_primary']};
        }}
        
        /* Scrollbar */
        QScrollBar:vertical {{
            background-color: {theme['bg_secondary']};
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['border_medium']};
            min-height: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['border_dark']};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {theme['bg_secondary']};
            height: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme['border_medium']};
            min-width: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme['border_dark']};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {theme['bg_tertiary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border_medium']};
            border-radius: 4px;
            padding: 5px;
        }}
        """
