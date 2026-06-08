"""Custom exceptions for RailScan Pro."""


class RailScanError(Exception):
    """Base exception for RailScan Pro errors."""


class ConfigError(RailScanError):
    """Raised when a RailScan configuration file is missing or invalid."""


class SerialClientError(RailScanError):
    """Raised when STOP serial communication fails."""


class CameraError(RailScanError):
    """Raised when camera configuration or capture fails."""


class InferenceError(RailScanError):
    """Raised when model configuration, preprocessing, or inference fails."""


class DecisionError(RailScanError):
    """Raised when decision configuration or update inputs are invalid."""


class DetectionAdapterError(RailScanError):
    """Raised when raw detection postprocessing inputs are invalid."""


class RuntimePipelineError(RailScanError):
    """Raised when safe runtime configuration or orchestration fails."""
