interface SectionHeaderProps {
  badge?: string
  title: string
  subtitle?: string
  center?: boolean
}

export default function SectionHeader({ badge, title, subtitle, center = true }: SectionHeaderProps) {
  return (
    <div className={`mb-12 md:mb-16 ${center ? 'text-center' : ''}`}>
      {badge && (
        <span className="inline-block px-4 py-1.5 mb-4 text-xs font-semibold tracking-widest uppercase rounded-full bg-cyan-glow/10 text-cyan-glow border border-cyan-glow/20">
          {badge}
        </span>
      )}
      <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-white leading-tight">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-4 text-base sm:text-lg text-gray-400 max-w-2xl leading-relaxed" style={center ? { margin: '1rem auto 0' } : {}}>
          {subtitle}
        </p>
      )}
    </div>
  )
}
