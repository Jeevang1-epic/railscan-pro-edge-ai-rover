import type { ReactNode } from 'react'
import SectionWrapper from './SectionWrapper'
import SectionHeader from './SectionHeader'
import { PIPELINE_STEPS } from '../constants'

const STEP_ICONS: Record<string, ReactNode> = {
  camera: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z" />
      <circle cx="12" cy="13" r="4" />
    </svg>
  ),
  cpu: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <line x1="9" y1="1" x2="9" y2="4" /><line x1="15" y1="1" x2="15" y2="4" />
      <line x1="9" y1="20" x2="9" y2="23" /><line x1="15" y1="20" x2="15" y2="23" />
      <line x1="20" y1="9" x2="23" y2="9" /><line x1="20" y1="14" x2="23" y2="14" />
      <line x1="1" y1="9" x2="4" y2="9" /><line x1="1" y1="14" x2="4" y2="14" />
    </svg>
  ),
  search: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  ),
  shield: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  ),
  lock: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0110 0v4" />
    </svg>
  ),
  chip: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="5" y="5" width="14" height="14" rx="2" />
      <path d="M8 1v3M16 1v3M8 20v3M16 20v3M1 8h3M1 16h3M20 8h3M20 16h3" />
    </svg>
  ),
}

const STEP_COLORS = [
  'from-cyan-glow/20 to-cyan-glow/5',
  'from-blue-glow/20 to-blue-glow/5',
  'from-cyan-glow/20 to-cyan-glow/5',
  'from-blue-glow/20 to-blue-glow/5',
  'from-amber-safety/20 to-amber-safety/5',
  'from-amber-safety/20 to-amber-safety/5',
]

const STEP_BORDER_COLORS = [
  'border-cyan-glow/20',
  'border-blue-glow/20',
  'border-cyan-glow/20',
  'border-blue-glow/20',
  'border-amber-safety/20',
  'border-amber-safety/20',
]

const STEP_TEXT_COLORS = [
  'text-cyan-glow',
  'text-blue-glow',
  'text-cyan-glow',
  'text-blue-glow',
  'text-amber-safety',
  'text-amber-safety',
]

export default function Architecture() {
  return (
    <SectionWrapper id="architecture" className="bg-grid-dense">
      <SectionHeader
        badge="System Architecture"
        title="End-to-End Pipeline"
        subtitle="A clear flow from camera input through AI inference to guarded motor control."
      />

      {/* Pipeline */}
      <div className="relative max-w-3xl mx-auto">
        {/* Vertical connector line */}
        <div className="absolute left-8 md:left-10 top-0 bottom-0 w-px bg-gradient-to-b from-cyan-glow/30 via-blue-glow/20 to-amber-safety/30 hidden sm:block" />

        <div className="space-y-4">
          {PIPELINE_STEPS.map((step, i) => (
            <div key={step.label} className="relative flex items-start gap-4 sm:gap-6 group">
              {/* Node dot */}
              <div className={`relative z-10 flex-shrink-0 w-16 h-16 md:w-20 md:h-20 rounded-xl bg-gradient-to-br ${STEP_COLORS[i]} border ${STEP_BORDER_COLORS[i]} flex items-center justify-center ${STEP_TEXT_COLORS[i]} group-hover:scale-105 transition-transform duration-300`}>
                {STEP_ICONS[step.icon]}
              </div>

              {/* Content */}
              <div className="flex-1 glass-card rounded-xl px-5 py-4 border border-white/5 group-hover:border-white/10 transition-colors duration-300">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-gray-500 tracking-wider uppercase">
                    Step {String(i + 1).padStart(2, '0')}
                  </span>
                  {i === 4 && (
                    <span className="px-2 py-0.5 text-[9px] font-mono tracking-wider uppercase rounded-full bg-amber-safety/10 text-amber-safety border border-amber-safety/20">
                      SAFETY GATED
                    </span>
                  )}
                </div>
                <h3 className="mt-1.5 text-base md:text-lg font-semibold text-white">{step.label}</h3>
              </div>

              {/* Arrow between steps */}
              {i < PIPELINE_STEPS.length - 1 && (
                <div className="absolute left-8 md:left-10 -bottom-2 w-px h-4 hidden sm:block">
                  <svg width="8" height="12" viewBox="0 0 8 12" className="absolute left-1/2 -translate-x-1/2 top-full text-cyan-glow/30">
                    <path d="M4 0 L4 8 L1 5 M4 8 L7 5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Architecture labels */}
      <div className="mt-12 flex flex-wrap justify-center gap-3">
        <ArchLabel color="cyan">Laptop / Edge Device</ArchLabel>
        <ArchLabel color="amber">Arduino UNO</ArchLabel>
        <ArchLabel color="gray">USB Serial Link</ArchLabel>
      </div>
    </SectionWrapper>
  )
}

function ArchLabel({ children, color }: { children: string; color: string }) {
  const styles: Record<string, string> = {
    cyan: 'bg-cyan-glow/8 text-cyan-glow border-cyan-glow/20',
    amber: 'bg-amber-safety/8 text-amber-safety border-amber-safety/20',
    gray: 'bg-white/5 text-gray-400 border-white/10',
  }

  return (
    <span className={`px-4 py-1.5 text-xs font-mono tracking-wider uppercase rounded-full border ${styles[color]}`}>
      {children}
    </span>
  )
}
