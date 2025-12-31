"""
Comprehensive error handling framework for AnomReceipt.
Ensures application never crashes and always provides user-friendly feedback.
"""

import sys
import traceback
import functools
from typing import Callable, Any, Optional, Type
from PySide6.QtWidgets import QMessageBox
from .logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """
    Central error handler for the application.
    Captures all exceptions and provides user-friendly messages.
    """
    
    @staticmethod
    def handle_exception(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback
    ) -> None:
        """
        Global exception handler for uncaught exceptions.
        
        Args:
            exc_type: Exception type
            exc_value: Exception instance
            exc_traceback: Traceback object
        """
        # Don't handle keyboard interrupts
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the full exception
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Get error message
        error_msg = str(exc_value) if exc_value else "Unknown error"
        
        # Show user-friendly message
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Application Error")
            msg_box.setText("An unexpected error occurred")
            msg_box.setInformativeText(
                f"{exc_type.__name__}: {error_msg}\n\n"
                "The error has been logged. The application will continue running."
            )
            msg_box.setDetailedText(
                "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception as e:
            # Fallback if GUI message fails
            logger.error(f"Failed to show error dialog: {e}")
            print(f"\nCRITICAL ERROR: {exc_type.__name__}: {error_msg}")
    
    @staticmethod
    def show_error(
        title: str,
        message: str,
        details: Optional[str] = None,
        parent=None
    ) -> None:
        """
        Show user-friendly error message.
        
        Args:
            title: Error dialog title
            message: Main error message
            details: Optional detailed information
            parent: Parent widget
        """
        try:
            logger.error(f"{title}: {message}")
            if details:
                logger.error(f"Details: {details}")
            
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if details:
                msg_box.setDetailedText(details)
            
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception as e:
            logger.error(f"Failed to show error dialog: {e}")
            print(f"\nERROR: {title}: {message}")
    
    @staticmethod
    def show_warning(
        title: str,
        message: str,
        parent=None
    ) -> None:
        """
        Show user-friendly warning message.
        
        Args:
            title: Warning dialog title
            message: Warning message
            parent: Parent widget
        """
        try:
            logger.warning(f"{title}: {message}")
            
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception as e:
            logger.error(f"Failed to show warning dialog: {e}")
            print(f"\nWARNING: {title}: {message}")
    
    @staticmethod
    def show_info(
        title: str,
        message: str,
        parent=None
    ) -> None:
        """
        Show information message.
        
        Args:
            title: Info dialog title
            message: Information message
            parent: Parent widget
        """
        try:
            logger.info(f"{title}: {message}")
            
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception as e:
            logger.error(f"Failed to show info dialog: {e}")
            print(f"\nINFO: {title}: {message}")
    
    @staticmethod
    def show_success(
        title: str,
        message: str,
        parent=None
    ) -> None:
        """
        Show success message.
        
        Args:
            title: Success dialog title
            message: Success message
            parent: Parent widget
        """
        try:
            logger.info(f"{title}: {message}")
            
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception as e:
            logger.error(f"Failed to show success dialog: {e}")
            print(f"\nSUCCESS: {title}: {message}")


def with_error_handling(
    error_title: str = "Operation Failed",
    error_message: str = "An error occurred while performing this operation",
    show_user_message: bool = True,
    default_return: Any = None
):
    """
    Decorator to wrap functions with error handling.
    
    Args:
        error_title: Title for error dialog
        error_message: User-friendly error message
        show_user_message: Whether to show message to user
        default_return: Value to return on error
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {e}",
                    exc_info=True
                )
                
                if show_user_message:
                    error_details = f"{type(e).__name__}: {str(e)}"
                    ErrorHandler.show_error(
                        error_title,
                        f"{error_message}\n\nWhat you can do:\n"
                        "• Check the log file for details\n"
                        "• Try the operation again\n"
                        "• Restart the application if problems persist",
                        details=error_details
                    )
                
                return default_return
        
        return wrapper
    return decorator


def safe_execute(
    operation: Callable,
    error_title: str = "Operation Failed",
    error_message: str = "An error occurred",
    default_return: Any = None,
    show_user_message: bool = True
) -> Any:
    """
    Safely execute an operation with error handling.
    
    Args:
        operation: Function to execute
        error_title: Title for error dialog
        error_message: User-friendly error message
        default_return: Value to return on error
        show_user_message: Whether to show message to user
    
    Returns:
        Operation result or default_return on error
    """
    try:
        return operation()
    except Exception as e:
        logger.error(
            f"Error in safe_execute: {e}",
            exc_info=True
        )
        
        if show_user_message:
            error_details = f"{type(e).__name__}: {str(e)}"
            ErrorHandler.show_error(
                error_title,
                f"{error_message}\n\nWhat you can do:\n"
                "• Check the log file for details\n"
                "• Try the operation again\n"
                "• Restart the application if problems persist",
                details=error_details
            )
        
        return default_return
