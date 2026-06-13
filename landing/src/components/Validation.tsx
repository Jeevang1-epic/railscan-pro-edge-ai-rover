import SectionWrapper from './SectionWrapper'
import SectionHeader from './SectionHeader'
import { VALIDATION_ITEMS } from '../constants'

export default function Validation() {
  const completed = VALIDATION_ITEMS.filter(v => v.color === 'green').length
  const pending = VALIDATION_ITEMS.filter(v => v.color === 'amber').length

  return (
    <SectionWrapper id="validation">
      <SectionHeader
        badge="Validation & Testing"
        title="Honest Status Report"
        subtitle="We believe in transparency. Here's exactly what's been validated and what's still pending."
      />

      {/* Summary stats */}
      <div className="flex flex-wrap justify-center gap-4 mb-10">
        <StatPill value={`${completed}`} label="Completed" color="green" />
        <StatPill value={`${pending}`} label="Pending" color="amber" />
        <StatPill value="100+" label="Automated Tests" color="cyan" />
      </div>

      {/* Validation grid */}
      <div className="grid sm:grid-cols-2 gap-3 max-w-3xl mx-auto">
        {VALIDATION_ITEMS.map((item) => (
          <div
            key={item.label}
            className="glass-card rounded-xl px-5 py-4 flex items-center gap-4 hover:border-white/10 transition-colors"
          >
            {/* Status indicator */}
            <div className={`flex-shrink-0 w-3 h-3 rounded-full ${
              item.color === 'green' ? 'bg-green-pass shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-amber-safety shadow-[0_0_8px_rgba(245,158,11,0.3)]'
            }`} />

            {/* Label */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{item.label}</p>
            </div>

            {/* Status badge */}
            <span className={`flex-shrink-0 px-3 py-1 text-[10px] font-mono tracking-wider uppercase rounded-full border ${
              item.color === 'green'
                ? 'bg-green-pass/8 text-green-pass border-green-pass/20'
                : 'bg-amber-safety/8 text-amber-safety border-amber-safety/20'
            }`}>
              {item.status}
            </span>
          </div>
        ))}
      </div>

      {/* Honest disclaimer */}
      <div className="mt-10 text-center">
        <p className="text-xs text-gray-500 font-mono max-w-lg mx-auto leading-relaxed">
          This is a proof-of-concept. Real camera, trained ONNX model, and hardware validation are pending next-stage work. No claims of being a certified railway product.
        </p>
      </div>
    </SectionWrapper>
  )
}

function StatPill({ value, label, color }: { value: string; label: string; color: string }) {
  const styles: Record<string, string> = {
    green: 'bg-green-pass/8 text-green-pass border-green-pass/15',
    amber: 'bg-amber-safety/8 text-amber-safety border-amber-safety/15',
    cyan: 'bg-cyan-glow/8 text-cyan-glow border-cyan-glow/15',
  }

  return (
    <div className={`px-5 py-2.5 rounded-full border ${styles[color]} flex items-center gap-2.5`}>
      <span className="text-xl font-bold">{value}</span>
      <span className="text-xs font-medium opacity-80">{label}</span>
    </div>
  )
}
