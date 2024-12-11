"use client"

import { motion } from "framer-motion"
import React, { useEffect, useRef } from "react"

interface BackgroundGradientProps {
  children: React.ReactNode
  className?: string
  containerClassName?: string
  animate?: boolean
}

export const BackgroundGradient: React.FC<BackgroundGradientProps> = ({
  children,
  className = "",
  containerClassName = "",
  animate = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!animate || !containerRef.current) return

    const handleMouseMove = (e: MouseEvent) => {
      const container = containerRef.current
      if (!container) return

      const { left, top } = container.getBoundingClientRect()
      const x = e.clientX - left
      const y = e.clientY - top

      container.style.setProperty("--x", `${x}px`)
      container.style.setProperty("--y", `${y}px`)
    }

    window.addEventListener("mousemove", handleMouseMove)

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
    }
  }, [animate])

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden bg-background ${containerClassName}`}
    >
      <motion.div
        className={`absolute inset-0 z-0 transition-opacity duration-500 ${
          animate ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background:
            "radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(var(--color-primary), 0.1) 0%, transparent 80%)",
        }}
        initial={false}
        animate={animate ? { opacity: 1 } : { opacity: 0 }}
      />
      <div className={`relative z-10 ${className}`}>{children}</div>
    </div>
  )
}
