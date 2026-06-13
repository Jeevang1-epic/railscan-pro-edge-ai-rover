import { GITHUB_URL, DEMO_VIDEO_URL, STATUS_ITEMS } from '../constants'

export default function Hero() {
  return (
    <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background layers */}
      <div className="absolute inset-0 bg-rail-950" />
      <div className="absolute inset-0 bg-grid opacity-60" />

      {/* Radial glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-radial from-cyan-glow/8 via-blue-glow/4 to-transparent rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-48 bg-gradient-to-t from-rail-950 to-transparent" />

      {/* Decorative rails */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-glow/30 to-transparent" />
      <div className="absolute bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-safety/20 to-transparent" />

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Text */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div className="animate-fade-in inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full bg-cyan-glow/8 border border-cyan-glow/15">
              <span className="w-2 h-2 rounded-full bg-green-pass animate-pulse" />
              <span className="text-xs font-medium tracking-wider uppercase text-cyan-glow/90">
                Proof-of-Concept · Safe Software Demo
              </span>
            </div>

            {/* Title */}
            <h1 className="animate-fade-in-up text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.05]">
              <span className="text-white">Rail</span>
              <span className="text-gradient">Scan</span>
              <span className="text-white"> Pro</span>
            </h1>

            {/* Subtitle */}
            <p className="animate-fade-in-up delay-200 mt-4 text-xl sm:text-2xl font-medium text-gray-300 tracking-tight">
              Edge-AI Railway Track Inspection Rover
            </p>

            {/* Tagline */}
            <p className="animate-fade-in-up delay-300 mt-5 text-base sm:text-lg text-gray-400 leading-relaxed max-w-xl mx-auto lg:mx-0">
              Detect visible track defects locally. Decide safely. Stop through a guarded Arduino actuation layer.
            </p>

            {/* CTA Buttons */}
            <div className="animate-fade-in-up delay-400 mt-8 flex flex-col sm:flex-row gap-3 justify-center lg:justify-start">
              <a
                href={DEMO_VIDEO_URL}
                className="group inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-semibold rounded-xl bg-gradient-to-r from-cyan-glow to-blue-glow text-white shadow-lg shadow-cyan-glow/25 hover:shadow-cyan-glow/40 transition-all duration-300 hover:-translate-y-0.5"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                Watch Demo
              </a>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-semibold rounded-xl bg-white/8 text-white border border-white/15 hover:bg-white/12 hover:border-white/25 transition-all duration-300 hover:-translate-y-0.5"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                View GitHub
              </a>
            </div>
          </div>

          {/* Right: Visual */}
          <div className="animate-fade-in-up delay-300 relative flex justify-center lg:justify-end">
            <HeroVisual />
          </div>
        </div>
      </div>
    </section>
  )
}

function HeroVisual() {
  return (
    <div className="relative w-full max-w-md">
      {/* Outer glow ring */}
      <div className="absolute -inset-4 rounded-2xl bg-gradient-to-br from-cyan-glow/10 via-transparent to-blue-glow/10 blur-xl" />

      {/* Main card */}
      <div className="relative glass-card rounded-2xl p-6 glow-border animate-pulse-glow">
        {/* Header bar */}
        <div className="flex items-center gap-2 mb-5">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-stop/60" />
            <div className="w-3 h-3 rounded-full bg-amber-safety/60" />
            <div className="w-3 h-3 rounded-full bg-green-pass/60" />
          </div>
          <span className="ml-2 text-xs font-mono text-gray-500">railscan-pro · system-status</span>
        </div>

        {/* Rover schematic */}
        <div className="relative mb-5 p-4 rounded-xl bg-rail-950/80 border border-cyan-glow/8">
          <RoverSVG />
        </div>

        {/* Status grid */}
        <div className="grid grid-cols-2 gap-2.5">
          {STATUS_ITEMS.map((item) => (
            <StatusBadge key={item.label} {...item} />
          ))}
        </div>

        {/* Proof-of-concept label */}
        <div className="mt-4 pt-3 border-t border-white/5 text-center">
          <span className="text-[10px] font-mono tracking-wider uppercase text-gray-500">
            proof-of-concept · safe software demo
          </span>
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ label, value, color }: { label: string; value: string; color: string }) {
  const colorMap: Record<string, string> = {
    cyan: 'text-cyan-glow border-cyan-glow/20 bg-cyan-glow/5',
    blue: 'text-blue-glow border-blue-glow/20 bg-blue-glow/5',
    amber: 'text-amber-safety border-amber-safety/20 bg-amber-safety/5',
    green: 'text-green-pass border-green-pass/20 bg-green-pass/5',
  }

  return (
    <div className={`px-3 py-2.5 rounded-lg border ${colorMap[color]}`}>
      <div className="text-[10px] font-mono uppercase tracking-wider opacity-60 mb-0.5">{label}</div>
      <div className="text-sm font-semibold">{value}</div>
    </div>
  )
}

function RoverSVG() {
  return (
    <svg viewBox="0 0 320 140" className="w-full" fill="none">
      {/* Track lines */}
      <line x1="0" y1="120" x2="320" y2="120" stroke="rgba(6,182,212,0.15)" strokeWidth="2" />
      <line x1="0" y1="125" x2="320" y2="125" stroke="rgba(6,182,212,0.15)" strokeWidth="2" />

      {/* Track ties */}
      {[40, 80, 120, 160, 200, 240, 280].map((x) => (
        <rect key={x} x={x - 3} y="117" width="6" height="12" rx="1" fill="rgba(6,182,212,0.08)" />
      ))}

      {/* Scan beam */}
      <path d="M 145 65 L 110 115 L 210 115 L 175 65 Z" fill="rgba(6,182,212,0.06)" stroke="rgba(6,182,212,0.2)" strokeWidth="1" strokeDasharray="4 3" />

      {/* Detection highlight */}
      <rect x="140" y="108" width="40" height="8" rx="2" fill="rgba(245,158,11,0.15)" stroke="rgba(245,158,11,0.4)" strokeWidth="1">
        <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite" />
      </rect>

      {/* Rover body */}
      <rect x="120" y="40" width="80" height="35" rx="6" fill="rgba(17,24,39,0.9)" stroke="rgba(6,182,212,0.4)" strokeWidth="1.5" />

      {/* Camera lens */}
      <circle cx="160" cy="55" r="8" fill="rgba(6,182,212,0.15)" stroke="rgba(6,182,212,0.5)" strokeWidth="1.5" />
      <circle cx="160" cy="55" r="3" fill="rgba(6,182,212,0.6)">
        <animate attributeName="r" values="3;4;3" dur="2s" repeatCount="indefinite" />
      </circle>

      {/* Antenna */}
      <line x1="145" y1="40" x2="140" y2="22" stroke="rgba(6,182,212,0.3)" strokeWidth="1.5" />
      <circle cx="140" cy="20" r="3" fill="rgba(6,182,212,0.4)">
        <animate attributeName="opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite" />
      </circle>

      {/* Status LED */}
      <circle cx="188" cy="50" r="3" fill="rgba(34,197,94,0.8)">
        <animate attributeName="opacity" values="1;0.3;1" dur="1s" repeatCount="indefinite" />
      </circle>

      {/* Wheels */}
      <circle cx="132" cy="82" r="9" fill="rgba(17,24,39,0.9)" stroke="rgba(100,116,139,0.4)" strokeWidth="2" />
      <circle cx="132" cy="82" r="4" fill="rgba(100,116,139,0.2)" />
      <circle cx="188" cy="82" r="9" fill="rgba(17,24,39,0.9)" stroke="rgba(100,116,139,0.4)" strokeWidth="2" />
      <circle cx="188" cy="82" r="4" fill="rgba(100,116,139,0.2)" />

      {/* Chassis connection */}
      <rect x="128" y="72" width="64" height="6" rx="2" fill="rgba(17,24,39,0.8)" stroke="rgba(100,116,139,0.3)" strokeWidth="1" />

      {/* EDGE-AI label */}
      <text x="160" y="62" textAnchor="middle" fill="rgba(6,182,212,0.5)" fontSize="6" fontFamily="monospace" fontWeight="600">EDGE-AI</text>

      {/* Data signals */}
      <line x1="200" y1="55" x2="240" y2="55" stroke="rgba(6,182,212,0.2)" strokeWidth="1" strokeDasharray="3 3">
        <animate attributeName="stroke-dashoffset" values="6;0" dur="1s" repeatCount="indefinite" />
      </line>
      <text x="255" y="58" fill="rgba(6,182,212,0.3)" fontSize="7" fontFamily="monospace">TX</text>

      <line x1="200" y1="62" x2="240" y2="62" stroke="rgba(245,158,11,0.2)" strokeWidth="1" strokeDasharray="3 3">
        <animate attributeName="stroke-dashoffset" values="0;6" dur="1s" repeatCount="indefinite" />
      </line>
      <text x="255" y="65" fill="rgba(245,158,11,0.3)" fontSize="7" fontFamily="monospace">RX</text>
    </svg>
  )
}
