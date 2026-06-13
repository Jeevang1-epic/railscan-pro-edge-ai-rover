import { useEffect, useRef, useState } from 'react'

/**
 * Intersection Observer hook for scroll-triggered animations.
 * Returns [ref, isVisible] — attach ref to the element you want to observe.
 */
export function useInView(threshold = 0.15, rootMargin = '0px') {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(el) // only animate once
        }
      },
      { threshold, rootMargin }
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [threshold, rootMargin])

  return [ref, isVisible] as const
}
