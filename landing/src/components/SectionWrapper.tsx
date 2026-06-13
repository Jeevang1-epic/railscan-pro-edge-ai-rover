import type { ReactNode } from 'react'
import { useInView } from '../hooks/useInView'

interface SectionWrapperProps {
  id: string
  children: ReactNode
  className?: string
  noPadding?: boolean
}

export default function SectionWrapper({ id, children, className = '', noPadding }: SectionWrapperProps) {
  const [ref, isVisible] = useInView(0.1)

  return (
    <section
      id={id}
      ref={ref}
      className={`
        relative
        ${noPadding ? '' : 'py-20 md:py-28 lg:py-32 px-4 sm:px-6 lg:px-8'}
        ${isVisible ? 'animate-fade-in-up' : 'opacity-0'}
        ${className}
      `}
    >
      <div className="max-w-6xl mx-auto relative z-10">
        {children}
      </div>
    </section>
  )
}
