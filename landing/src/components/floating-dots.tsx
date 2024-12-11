'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface FloatingDot {
  x: string
  y: string
  delay: number
}

const floatingDots: FloatingDot[] = [
  { x: '10%', y: '20%', delay: 0 },
  { x: '90%', y: '60%', delay: 0.2 },
  { x: '30%', y: '70%', delay: 0.4 },
  { x: '70%', y: '10%', delay: 0.6 },
  { x: '50%', y: '40%', delay: 0.8 },
]

export const FloatingDots: React.FC = () => {
  return (
    <>
      {floatingDots.map((dot, index) => (
        <motion.div
          key={index}
          className="absolute w-2 h-2 bg-primary rounded-full"
          style={{ left: dot.x, top: dot.y }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            delay: dot.delay,
          }}
        />
      ))}
    </>
  )
}

