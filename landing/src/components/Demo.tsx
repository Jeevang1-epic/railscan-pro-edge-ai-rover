import { useState } from 'react'
import SectionWrapper from './SectionWrapper'
import SectionHeader from './SectionHeader'
import { DEMO_COMMANDS } from '../constants'

export default function Demo() {
  return (
    <SectionWrapper id="demo">
      <SectionHeader
        badge="Safe Demo"
        title="Run It Yourself"
        subtitle="All demos run in safe dry-run mode. The simulated defect triggers the decision path, but STOP remains dry-run unless explicit safety flags are provided."
      />

      <div className="space-y-5 max-w-3xl mx-auto">
        {DEMO_COMMANDS.map((cmd, i) => (
          <TerminalCard key={i} {...cmd} index={i} />
        ))}
      </div>

      {/* Safety note */}
      <div className="mt-10 max-w-3xl mx-auto">
        <div className="glass-card-amber rounded-xl p-5 flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-amber-safety/10 border border-amber-safety/20 flex items-center justify-center text-amber-safety">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="M12 8v4" strokeLinecap="round" />
              <circle cx="12" cy="16" r="0.5" fill="currentColor" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-amber-safety mb-1">Safety by Default</p>
            <p className="text-sm text-gray-400 leading-relaxed">
              STOP remains dry-run unless explicit safety flags are provided. This is a safe software demo — real STOP requires explicit safety flags, wheels-lifted confirmation, and physical rover preparation.
            </p>
          </div>
        </div>
      </div>
    </SectionWrapper>
  )
}

function TerminalCard({ title, desc, cmd, index }: { title: string; desc: string; cmd: string; index: number }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(cmd).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="glass-card rounded-xl overflow-hidden group hover:border-cyan-glow/20 transition-all duration-300">
      {/* Header */}
      <div className="px-5 py-3 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-stop/50" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-safety/50" />
            <div className="w-2.5 h-2.5 rounded-full bg-green-pass/50" />
          </div>
          <span className="text-xs font-mono text-gray-500">demo-{String(index + 1).padStart(2, '0')}</span>
        </div>
        <span className="text-xs font-semibold text-gray-400">{title}</span>
      </div>

      {/* Description */}
      <div className="px-5 py-2.5 border-b border-white/3">
        <p className="text-xs text-gray-500">{desc}</p>
      </div>

      {/* Command */}
      <div className="px-5 py-4 flex items-center gap-3 bg-rail-950/50">
        <span className="text-green-pass/60 font-mono text-sm select-none">$</span>
        <code className="flex-1 text-sm font-mono text-cyan-glow/90 break-all">{cmd}</code>
        <button
          onClick={handleCopy}
          className="flex-shrink-0 px-3 py-1.5 text-xs font-mono rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors border border-white/5 hover:border-white/15"
          title="Copy command"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>
    </div>
  )
}
