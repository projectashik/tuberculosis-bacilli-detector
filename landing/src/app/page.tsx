import Contact from "@/components/Contact"
import Features from "@/components/Features"
import Hero from "@/components/Hero"
import HowItWorks from "@/components/HowItWorks"

export default function Home() {
  return (
    <div className='min-h-screen bg-gray-50'>
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Contact />
      </main>
    </div>
  )
}
