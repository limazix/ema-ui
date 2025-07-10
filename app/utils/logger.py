import inspect
import logging

from app.utils.config_handler import ConfigHandler


class Logger:
    def __init__(self, name=None):
        self._logger = logging.getLogger(name if name else self._get_calling_module_name())
        self._configure_logger()

    def _get_calling_module_name(self):
        frame = inspect.currentframe()
        if frame is None:
            return __name__
        outer_frames = inspect.getouterframes(frame, 2)
        if len(outer_frames) > 2:
            # The third frame (index 2) is the one calling Logger()
            calling_frame = outer_frames[2]
            return inspect.getmodule(calling_frame[0]).__name__
        return __name__

    def _configure_logger(self):
        config_handler = ConfigHandler()  # Assuming ConfigHandler is initialized elsewhere or handles its own instance
        log_level = config_handler.get_config("logging", "level", default="INFO").upper()
        log_format = config_handler.get_config("logging", "format", default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        level = getattr(logging, log_level, logging.INFO)
        self._logger.setLevel(level)

        # Avoid adding duplicate handlers if the logger is already configured
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def debug(self, message, *args, **kwargs):
        self._log_with_context(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log_with_context(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log_with_context(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log_with_context(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log_with_context(logging.CRITICAL, message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        self._log_with_context(logging.ERROR, message, exc_info=True, *args, **kwargs)

    def _log_with_context(self, level, message, *args, **kwargs):
        frame = inspect.currentframe()
        if frame is None:
            self._logger.log(level, message, *args, **kwargs)
            return

        outer_frames = inspect.getouterframes(frame, 2)
        # The third frame (index 2) is the one calling the log method (e.g., info, debug)
        if len(outer_frames) > 2:
            calling_frame = outer_frames[2]
            class_name = None
            method_name = calling_frame[3]  # Function/method name

            # Attempt to get the class name if inside a method
            if 'self' in calling_frame[0].f_locals:
                class_name = calling_frame[0].f_locals['self'].__class__.__name__
            elif 'cls' in calling_frame[0].f_locals:
                class_name = calling_frame[0].f_locals['cls'].__name__

            context = f"{class_name}.{method_name}" if class_name else method_name
            full_message = f"[{context}] {message}"
            self._logger.log(level, full_message, *args, **kwargs)
        else:
            self._logger.log(level, message, *args, **kwargs)
