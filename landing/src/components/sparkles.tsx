"use client"

import { cn } from "@/lib/utils"
import { useEffect, useRef, useState } from "react"

export const SparklesCore = (props: {
  id?: string
  className?: string
  background?: string
  minSize?: number
  maxSize?: number
  particleDensity?: number
  particleColor?: string
  particleSpeed?: number
}) => {
  const {
    id,
    className,
    background = "transparent",
    minSize = 0.4,
    maxSize = 1,
    particleDensity = 100,
    particleColor = "#FFF",
    particleSpeed = 1,
  } = props

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [context, setContext] = useState<CanvasRenderingContext2D | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current
      const ctx = canvas.getContext("2d")
      setContext(ctx)
    }
  }, [])

  useEffect(() => {
    if (!context) return

    const particles: Particle[] = []

    const Particle = class {
      x: number
      y: number
      size: number
      speedX: number
      speedY: number

      constructor() {
        this.x = Math.random() * context.canvas.width
        this.y = Math.random() * context.canvas.height
        this.size = Math.random() * (maxSize - minSize) + minSize
        this.speedX = Math.random() * particleSpeed - particleSpeed / 2
        this.speedY = Math.random() * particleSpeed - particleSpeed / 2
      }

      update() {
        this.x += this.speedX
        this.y += this.speedY

        if (this.x > context.canvas.width) {
          this.x = 0
        } else if (this.x < 0) {
          this.x = context.canvas.width
        }

        if (this.y > context.canvas.height) {
          this.y = 0
        } else if (this.y < 0) {
          this.y = context.canvas.height
        }
      }

      draw() {
        context.fillStyle = particleColor
        context.beginPath()
        context.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        context.fill()
      }
    }

    const handleResize = () => {
      if (canvasRef.current) {
        canvasRef.current.width = window.innerWidth
        canvasRef.current.height = window.innerHeight
      }
    }
    handleResize()
    window.addEventListener("resize", handleResize)

    for (let i = 0; i < particleDensity; i++) {
      particles.push(new Particle())
    }

    const animate = () => {
      context.clearRect(0, 0, context.canvas.width, context.canvas.height)
      for (let i = 0; i < particles.length; i++) {
        particles[i].update()
        particles[i].draw()
      }
      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", handleResize)
    }
  }, [context, maxSize, minSize, particleColor, particleDensity, particleSpeed])

  return (
    <canvas
      ref={canvasRef}
      id={id}
      className={cn("fixed inset-0 -z-10", className)}
      style={{ background }}
    />
  )
}
