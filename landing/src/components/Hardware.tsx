import SectionWrapper from './SectionWrapper'
import SectionHeader from './SectionHeader'
import { HARDWARE_ITEMS } from '../constants'

const HW_ICONS = [
  // 4WD chassis
  <svg key="chassis" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="2" y="8" width="20" height="8" rx="2" />
    <circle cx="6" cy="18" r="2" /><circle cx="18" cy="18" r="2" />
    <circle cx="6" cy="6" r="2" /><circle cx="18" cy="6" r="2" />
  </svg>,
  // Arduino
  <svg key="arduino" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <circle cx="12" cy="12" r="3" />
    <line x1="7" y1="5" x2="7" y2="3" /><line x1="12" y1="5" x2="12" y2="3" /><line x1="17" y1="5" x2="17" y2="3" />
    <line x1="7" y1="19" x2="7" y2="21" /><line x1="12" y1="19" x2="12" y2="21" /><line x1="17" y1="19" x2="17" y2="21" />
  </svg>,
  // L298N
  <svg key="l298n" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="4" y="4" width="16" height="16" rx="2" />
    <path d="M4 12h16" />
    <path d="M8 8h2M14 8h2M8 16h2M14 16h2" strokeLinecap="round" />
  </svg>,
  // DC motors
  <svg key="motors" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <circle cx="12" cy="12" r="8" />
    <circle cx="12" cy="12" r="3" />
    <path d="M12 4v2M12 18v2M4 12h2M18 12h2" strokeLinecap="round" />
  </svg>,
  // USB
  <svg key="usb" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M12 2v10" />
    <path d="M7 7l5 5 5-5" />
    <circle cx="12" cy="18" r="3" />
    <path d="M12 15v-3" />
    <circle cx="7" cy="10" r="1.5" fill="currentColor" />
    <circle cx="17" cy="10" r="1.5" />
  </svg>,
]

export default function Hardware() {
  return (
    <SectionWrapper id="hardware" className="bg-grid">
      <SectionHeader
        badge="Hardware Prototype"
        title="Built for Real-World Testing"
        subtitle="A modular rover platform designed for step-by-step hardware validation."
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
        {HARDWARE_ITEMS.map((item, i) => (
          <div
            key={item.name}
            className="glass-card rounded-xl p-5 hover:border-cyan-glow/20 transition-all duration-300 group hover:-translate-y-0.5"
          >
            <div className="w-12 h-12 rounded-xl bg-cyan-glow/8 border border-cyan-glow/15 flex items-center justify-center text-cyan-glow mb-4 group-hover:bg-cyan-glow/12 transition-colors">
              {HW_ICONS[i]}
            </div>
            <h3 className="text-base font-semibold text-white mb-1">{item.name}</h3>
            <p className="text-sm text-gray-500">{item.detail}</p>
          </div>
        ))}

        {/* Hardware note card */}
        <div className="glass-card-amber rounded-xl p-5 flex flex-col justify-center sm:col-span-2 lg:col-span-1">
          <div className="w-10 h-10 rounded-lg bg-amber-safety/10 border border-amber-safety/20 flex items-center justify-center text-amber-safety mb-3">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" strokeLinecap="round" />
              <line x1="12" y1="16" x2="12.01" y2="16" strokeLinecap="round" />
            </svg>
          </div>
          <p className="text-sm text-gray-400 leading-relaxed">
            Hardware validation is performed step-by-step with <span className="text-amber-safety font-medium">wheels lifted</span> before real STOP testing.
          </p>
        </div>
      </div>

      {/* Rover Diagram */}
      <div className="mt-12 max-w-2xl mx-auto">
        <div className="glass-card rounded-xl p-6 glow-border">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs font-mono text-gray-500 tracking-wider uppercase">System Wiring Overview</span>
          </div>
          <HardwareDiagram />
        </div>
      </div>
    </SectionWrapper>
  )
}

function HardwareDiagram() {
  return (
    <svg viewBox="0 0 500 160" className="w-full" fill="none">
      {/* Laptop */}
      <rect x="10" y="40" width="100" height="70" rx="6" fill="rgba(17,24,39,0.8)" stroke="rgba(6,182,212,0.3)" strokeWidth="1.5" />
      <text x="60" y="68" textAnchor="middle" fill="rgba(6,182,212,0.7)" fontSize="9" fontFamily="monospace" fontWeight="600">LAPTOP</text>
      <text x="60" y="82" textAnchor="middle" fill="rgba(148,163,184,0.5)" fontSize="7" fontFamily="monospace">AI + Decision</text>
      <text x="60" y="95" textAnchor="middle" fill="rgba(148,163,184,0.4)" fontSize="7" fontFamily="monospace">ONNX + YOLO</text>

      {/* USB arrow */}
      <line x1="115" y1="75" x2="175" y2="75" stroke="rgba(6,182,212,0.25)" strokeWidth="1.5" strokeDasharray="4 3">
        <animate attributeName="stroke-dashoffset" values="7;0" dur="1s" repeatCount="indefinite" />
      </line>
      <text x="145" y="68" textAnchor="middle" fill="rgba(148,163,184,0.4)" fontSize="7" fontFamily="monospace">USB</text>
      <polygon points="175,72 175,78 182,75" fill="rgba(6,182,212,0.3)" />

      {/* Arduino */}
      <rect x="185" y="40" width="100" height="70" rx="6" fill="rgba(17,24,39,0.8)" stroke="rgba(245,158,11,0.3)" strokeWidth="1.5" />
      <text x="235" y="68" textAnchor="middle" fill="rgba(245,158,11,0.7)" fontSize="9" fontFamily="monospace" fontWeight="600">ARDUINO</text>
      <text x="235" y="82" textAnchor="middle" fill="rgba(148,163,184,0.5)" fontSize="7" fontFamily="monospace">UNO</text>
      <text x="235" y="95" textAnchor="middle" fill="rgba(148,163,184,0.4)" fontSize="7" fontFamily="monospace">STOP Control</text>

      {/* Arrow to driver */}
      <line x1="290" y1="75" x2="345" y2="75" stroke="rgba(245,158,11,0.25)" strokeWidth="1.5" strokeDasharray="4 3">
        <animate attributeName="stroke-dashoffset" values="7;0" dur="0.8s" repeatCount="indefinite" />
      </line>
      <text x="317" y="68" textAnchor="middle" fill="rgba(148,163,184,0.4)" fontSize="7" fontFamily="monospace">PWM</text>
      <polygon points="345,72 345,78 352,75" fill="rgba(245,158,11,0.3)" />

      {/* L298N */}
      <rect x="355" y="40" width="100" height="70" rx="6" fill="rgba(17,24,39,0.8)" stroke="rgba(100,116,139,0.3)" strokeWidth="1.5" />
      <text x="405" y="68" textAnchor="middle" fill="rgba(148,163,184,0.6)" fontSize="9" fontFamily="monospace" fontWeight="600">L298N</text>
      <text x="405" y="82" textAnchor="middle" fill="rgba(148,163,184,0.5)" fontSize="7" fontFamily="monospace">Motor Driver</text>
      <text x="405" y="95" textAnchor="middle" fill="rgba(148,163,184,0.4)" fontSize="7" fontFamily="monospace">4× DC Motors</text>

      {/* Labels under */}
      <text x="60" y="135" textAnchor="middle" fill="rgba(6,182,212,0.4)" fontSize="8" fontFamily="monospace">Edge Device</text>
      <text x="235" y="135" textAnchor="middle" fill="rgba(245,158,11,0.4)" fontSize="8" fontFamily="monospace">Controller</text>
      <text x="405" y="135" textAnchor="middle" fill="rgba(148,163,184,0.35)" fontSize="8" fontFamily="monospace">Actuator</text>

      {/* Safety gate indicator */}
      <rect x="155" y="55" width="2" height="40" rx="1" fill="rgba(245,158,11,0.4)">
        <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" />
      </rect>
    </svg>
  )
}
