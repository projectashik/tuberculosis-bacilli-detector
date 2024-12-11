"use client"

import { motion } from "framer-motion"
import { Camera, Clock, Microscope, Server } from "lucide-react"

const features = [
  {
    icon: Microscope,
    title: "Advanced Microscopy",
    description:
      "High-precision microscope with motorized stage for accurate sample analysis.",
  },
  {
    icon: Camera,
    title: "Automated Imaging",
    description:
      "Captures high-resolution images every 3 seconds for comprehensive sample coverage.",
  },
  {
    icon: Server,
    title: "Secure Cloud Storage",
    description:
      "Images are securely stored in Azure Blob storage, organized by patient ID.",
  },
  {
    icon: Clock,
    title: "Real-time Analysis",
    description:
      "Immediate processing and analysis of captured images for quick results.",
  },
]

const FeatureItem = ({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ElementType
  title: string
  description: string
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: 0.1 }}
    className='bg-gray-50 p-6 rounded-lg shadow-md'
  >
    <Icon className='w-12 h-12 text-blue-600 mb-4' />
    <h3 className='text-xl font-semibold text-gray-900 mb-2'>{title}</h3>
    <p className='text-gray-600'>{description}</p>
  </motion.div>
)

export default function Features() {
  return (
    <section id='features' className='py-20 bg-white'>
      <div className='container mx-auto px-4'>
        <h2 className='text-3xl font-bold text-center text-gray-900 mb-12'>
          Key Features
        </h2>
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8'>
          {features.map((feature, index) => (
            <FeatureItem
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
