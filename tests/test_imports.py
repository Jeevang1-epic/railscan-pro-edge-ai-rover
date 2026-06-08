from pathlib import Path

import railscan
from railscan.camera import CameraConfig, RailScanCamera
from railscan.config import load_config
from railscan.decision import (
    DecisionConfig,
    DecisionResult,
    Detection,
    RailScanDecisionEngine,
)
from railscan.detection_adapter import (
    DetectionAdapterConfig,
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
)
from railscan.inference import InferenceConfig, RailScanInferenceEngine
from railscan.logger import setup_logging
from railscan.runtime import (
    RailScanRuntime,
    RuntimeConfig,
    RuntimeFrameResult,
    RuntimeSummary,
    StopActionResult,
)
from railscan.serial_client import RailScanSerialClient, SerialConfig

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_package_imports_work() -> None:
    assert railscan.load_config is load_config
    assert railscan.setup_logging is setup_logging
    assert issubclass(ConfigError, RailScanError)
    assert issubclass(CameraError, RailScanError)
    assert issubclass(InferenceError, RailScanError)
    assert issubclass(DecisionError, RailScanError)
    assert issubclass(DetectionAdapterError, RailScanError)
    assert issubclass(RuntimePipelineError, RailScanError)
    assert railscan.CameraConfig is CameraConfig
    assert railscan.RailScanCamera is RailScanCamera
    assert railscan.DecisionConfig is DecisionConfig
    assert railscan.DecisionResult is DecisionResult
    assert railscan.Detection is Detection
    assert railscan.RailScanDecisionEngine is RailScanDecisionEngine
    assert railscan.DetectionAdapterConfig is DetectionAdapterConfig
    assert railscan.YoloDetectionAdapter is YoloDetectionAdapter
    assert railscan.bbox_iou is bbox_iou
    assert railscan.cxcywh_to_xyxy is cxcywh_to_xyxy
    assert railscan.non_max_suppression is non_max_suppression
    assert railscan.InferenceConfig is InferenceConfig
    assert railscan.RailScanInferenceEngine is RailScanInferenceEngine
    assert railscan.RuntimeConfig is RuntimeConfig
    assert railscan.RuntimeFrameResult is RuntimeFrameResult
    assert railscan.RuntimeSummary is RuntimeSummary
    assert railscan.StopActionResult is StopActionResult
    assert railscan.RailScanRuntime is RailScanRuntime
    assert railscan.SerialConfig is SerialConfig
    assert railscan.RailScanSerialClient is RailScanSerialClient


def test_prompt_runtime_script_files_exist() -> None:
    assert (REPO_ROOT / "scripts" / "train_yolo.py").is_file()
    assert (REPO_ROOT / "scripts" / "export_onnx.py").is_file()
    assert (REPO_ROOT / "scripts" / "validate_model_artifact.py").is_file()
    assert (REPO_ROOT / "scripts" / "run_demo.py").is_file()
    assert (REPO_ROOT / "scripts" / "final_qa.py").is_file()
    assert (REPO_ROOT / "scripts" / "package_demo_artifacts.py").is_file()
    assert (REPO_ROOT / "requirements-train.txt").is_file()
