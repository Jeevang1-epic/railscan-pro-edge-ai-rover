import { GITHUB_URL } from '../constants'

export default function Footer() {
  return (
    <footer className="relative border-t border-white/5 bg-rail-950">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Left: Logo + team */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-glow to-blue-glow flex items-center justify-center">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <path d="M3 11L8 5L13 11" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <line x1="4" y1="14" x2="12" y2="14" stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </div>
            <div>
              <span className="text-white font-semibold text-sm">
                Rail<span className="text-cyan-glow">Scan</span> Pro
              </span>
              <p className="text-[10px] text-gray-500 font-mono">by Team Sentinals95</p>
            </div>
          </div>

          {/* Center: Links */}
          <div className="flex items-center gap-6">
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="text-xs text-gray-500 hover:text-cyan-glow transition-colors">
              GitHub
            </a>
            <a href="#demo" className="text-xs text-gray-500 hover:text-cyan-glow transition-colors">
              Demo
            </a>
            <a href="#architecture" className="text-xs text-gray-500 hover:text-cyan-glow transition-colors">
              Architecture
            </a>
            <a href="#validation" className="text-xs text-gray-500 hover:text-cyan-glow transition-colors">
              Validation
            </a>
          </div>

          {/* Right: Disclaimer */}
          <p className="text-[10px] text-gray-600 font-mono text-center md:text-right max-w-xs">
            Proof-of-concept · Not a certified railway product · Makers Conclave 2026
          </p>
        </div>

        {/* Bottom line */}
        <div className="mt-8 pt-6 border-t border-white/5 text-center">
          <p className="text-xs text-gray-600">
            © 2026 Team Sentinals95 · RailScan Pro · Safe Software Demo
          </p>
        </div>
      </div>
    </footer>
  )
}
