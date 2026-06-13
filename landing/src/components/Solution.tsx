import type { ReactNode } from 'react'
import SectionWrapper from './SectionWrapper'
import SectionHeader from './SectionHeader'
import { SOLUTION_CARDS } from '../constants'

const ICONS: Record<string, ReactNode> = {
  eye: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ),
  shield: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  zap: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  ),
}

const CARD_COLORS = [
  { bg: 'bg-cyan-glow/8', border: 'border-cyan-glow/15', text: 'text-cyan-glow', hover: 'hover:border-cyan-glow/30' },
  { bg: 'bg-blue-glow/8', border: 'border-blue-glow/15', text: 'text-blue-glow', hover: 'hover:border-blue-glow/30' },
  { bg: 'bg-amber-safety/8', border: 'border-amber-safety/15', text: 'text-amber-safety', hover: 'hover:border-amber-safety/30' },
]

export default function Solution() {
  return (
    <SectionWrapper id="solution">
      <SectionHeader
        badge="Our Approach"
        title="Split Architecture, Maximum Safety"
        subtitle="RailScan Pro combines local computer vision with embedded motor control. The laptop handles AI and decision-making. Arduino handles movement and STOP control."
      />

      <div className="grid md:grid-cols-3 gap-5">
        {SOLUTION_CARDS.map((card, i) => {
          const colors = CARD_COLORS[i]
          return (
            <div
              key={card.title}
              className={`glass-card rounded-xl p-6 border ${colors.border} ${colors.hover} transition-all duration-300 group hover:-translate-y-1`}
            >
              <div className={`w-14 h-14 rounded-xl ${colors.bg} border ${colors.border} flex items-center justify-center ${colors.text} mb-5 group-hover:scale-105 transition-transform duration-300`}>
                {ICONS[card.icon]}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{card.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{card.desc}</p>
            </div>
          )
        })}
      </div>

      {/* Bottom note */}
      <div className="mt-10 text-center">
        <p className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-amber-safety/8 border border-amber-safety/15 text-amber-safety text-xs font-mono tracking-wide">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" strokeLinecap="round" />
            <line x1="12" y1="17" x2="12.01" y2="17" strokeLinecap="round" />
          </svg>
          Real STOP requires explicit safety flags — disabled by default
        </p>
      </div>
    </SectionWrapper>
  )
}
