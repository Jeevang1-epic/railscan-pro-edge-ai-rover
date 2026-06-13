import SectionWrapper from './SectionWrapper'
import SectionHeader from './SectionHeader'

const PROBLEMS = [
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 8v4l2 2" strokeLinecap="round" />
      </svg>
    ),
    title: "Slow Manual Inspection",
    desc: "Human inspectors walk thousands of kilometres of track. It's time-consuming and impossible to scale."
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" strokeLinecap="round" />
        <line x1="12" y1="17" x2="12.01" y2="17" strokeLinecap="round" />
      </svg>
    ),
    title: "Visible Defects Go Unnoticed",
    desc: "Cracks, missing fasteners, surface damage, and obstacles can become dangerous if not detected early."
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
        <line x1="4" y1="22" x2="4" y2="15" />
      </svg>
    ),
    title: "Difficult to Scale",
    desc: "India's 68,000+ km railway network needs automated inspection that can keep pace with daily operations."
  },
]

export default function Problem() {
  return (
    <SectionWrapper id="problem" className="bg-grid">
      <SectionHeader
        badge="The Challenge"
        title="Why Railway Inspection Needs Automation"
        subtitle="Railway track inspection is slow, repetitive, and difficult to scale. Small visible defects can escalate into serious safety concerns."
      />

      <div className="grid md:grid-cols-3 gap-5">
        {PROBLEMS.map((item, i) => (
          <div
            key={item.title}
            className="glass-card rounded-xl p-6 hover:border-cyan-glow/25 transition-all duration-300 group"
            style={{ animationDelay: `${i * 120}ms` }}
          >
            <div className="w-12 h-12 rounded-xl bg-cyan-glow/8 border border-cyan-glow/15 flex items-center justify-center text-cyan-glow mb-4 group-hover:bg-cyan-glow/15 transition-colors duration-300">
              {item.icon}
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </SectionWrapper>
  )
}
