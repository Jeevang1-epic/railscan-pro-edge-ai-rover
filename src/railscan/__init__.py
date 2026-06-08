"""Foundation package for RailScan Pro."""

from railscan.camera import CameraConfig, FrameResult, RailScanCamera
from railscan.config import REQUIRED_CONFIG_SECTIONS, load_config, validate_config
from railscan.decision import (
    DecisionConfig,
    DecisionResult,
    Detection,
    RailScanDecisionEngine,
)
from railscan.detection_adapter import (
    DetectionAdapterConfig,
    ParsedCandidate,
    YoloDetectionAdapter,
    bbox_iou,
    cxcywh_to_xyxy,
    non_max_suppression,
)
from railscan.exceptions import (
    CameraError,
    ConfigError,
    DecisionError,
    DetectionAdapterError,
    InferenceError,
    RailScanError,
    RuntimePipelineError,
    SerialClientError,
)
from railscan.inference import InferenceConfig, InferenceResult, RailScanInferenceEngine
from railscan.logger import setup_logging
from railscan.runtime import (
    RailScanRuntime,
    RuntimeConfig,
    RuntimeFrameResult,
    RuntimeSummary,
    StopActionResult,
)
from railscan.serial_client import RailScanSerialClient, SerialConfig, StopResult

__all__ = [
    "CameraConfig",
    "CameraError",
    "ConfigError",
    "DecisionConfig",
    "DecisionError",
    "DecisionResult",
    "Detection",
    "DetectionAdapterConfig",
    "DetectionAdapterError",
    "FrameResult",
    "InferenceConfig",
    "InferenceError",
    "InferenceResult",
    "ParsedCandidate",
    "RailScanError",
    "RailScanCamera",
    "RailScanDecisionEngine",
    "RailScanInferenceEngine",
    "RailScanRuntime",
    "RailScanSerialClient",
    "REQUIRED_CONFIG_SECTIONS",
    "RuntimeConfig",
    "RuntimeFrameResult",
    "RuntimePipelineError",
    "RuntimeSummary",
    "SerialClientError",
    "SerialConfig",
    "StopActionResult",
    "StopResult",
    "YoloDetectionAdapter",
    "bbox_iou",
    "cxcywh_to_xyxy",
    "load_config",
    "non_max_suppression",
    "setup_logging",
    "validate_config",
]
