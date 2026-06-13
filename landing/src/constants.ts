// ─── RailScan Pro Constants ───

export const GITHUB_URL = "https://github.com/Jeevang1-epic/railscan-pro-edge-ai-rover"
export const DEMO_VIDEO_URL = "#"
export const DEPLOYED_URL = "#"

export const NAV_LINKS = [
  { label: "Problem", href: "#problem" },
  { label: "Solution", href: "#solution" },
  { label: "Architecture", href: "#architecture" },
  { label: "Demo", href: "#demo" },
  { label: "Hardware", href: "#hardware" },
  { label: "Validation", href: "#validation" },
] as const

export const STATUS_ITEMS = [
  { label: "Mode", value: "Safe Dry Run", color: "cyan" },
  { label: "Inference", value: "ONNX-ready", color: "blue" },
  { label: "STOP", value: "Safety Gated", color: "amber" },
  { label: "Tests", value: "100+ Passed", color: "green" },
] as const

export const SOLUTION_CARDS = [
  {
    icon: "eye",
    title: "Local Vision",
    desc: "Camera input processed through ONNX-ready inference with a YOLO-style detection adapter. All processing runs locally on the edge device.",
  },
  {
    icon: "shield",
    title: "Safety Decision Engine",
    desc: "Aggregates detection results and applies safety logic. Only triggers STOP when confidence thresholds are met and safety flags are explicitly enabled.",
  },
  {
    icon: "zap",
    title: "Arduino STOP Interface",
    desc: "Guarded serial communication to Arduino UNO + L298N motor driver. Real STOP requires explicit safety flags — disabled by default.",
  },
] as const

export const PIPELINE_STEPS = [
  { label: "Camera / Synthetic Frames", icon: "camera" },
  { label: "ONNX or Mock Inference", icon: "cpu" },
  { label: "YOLO-style Detection Adapter", icon: "search" },
  { label: "Safety Decision Engine", icon: "shield" },
  { label: "Guarded Serial STOP", icon: "lock" },
  { label: "Arduino + L298N Motor Control", icon: "chip" },
] as const

export const DEMO_COMMANDS = [
  {
    title: "Final QA Script",
    desc: "Run the complete quality-assurance test suite",
    cmd: "python scripts/final_qa.py",
  },
  {
    title: "Normal Dry-Run Demo",
    desc: "Run full pipeline with synthetic frames, mock inference, and serial dry-run",
    cmd: "python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5",
  },
  {
    title: "Simulated Defect Demo",
    desc: "Injects a simulated defect at frame 3 to test the decision path",
    cmd: "python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3",
  },
] as const

export const HARDWARE_ITEMS = [
  { name: "4WD Rover Chassis", detail: "Sturdy 4-wheel-drive platform" },
  { name: "Arduino UNO", detail: "Low-level motor + STOP control" },
  { name: "L298N Motor Driver", detail: "Dual H-bridge motor driver" },
  { name: "DC Gear Motors", detail: "4× geared DC motors" },
  { name: "USB Serial Link", detail: "Laptop ↔ Arduino communication" },
] as const

export const VALIDATION_ITEMS = [
  { label: "Safe runtime demo", status: "Completed", color: "green" },
  { label: "Simulated defect demo", status: "Completed", color: "green" },
  { label: "Final QA script", status: "Completed", color: "green" },
  { label: "Submission package", status: "Completed", color: "green" },
  { label: "100+ automated tests", status: "Completed", color: "green" },
  { label: "Real camera validation", status: "Pending Physical Validation", color: "amber" },
  { label: "Trained ONNX model", status: "Pending Physical Validation", color: "amber" },
  { label: "Real hardware STOP test", status: "Pending Physical Validation", color: "amber" },
] as const
