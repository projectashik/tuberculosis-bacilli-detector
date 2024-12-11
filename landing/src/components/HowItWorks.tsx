"use client"

import { motion } from "framer-motion"
import Image from "next/image"

const steps = [
  {
    title: "Sample Preparation",
    description:
      "Prepare the microscopic sample on a slide according to standard procedures.",
  },
  {
    title: "Load Sample",
    description: "Place the prepared slide into the CellSight device.",
  },
  {
    title: "Automated Scanning",
    description:
      "CellSight automatically scans the sample, capturing high-resolution images.",
  },
  {
    title: "Image Processing",
    description:
      "Images are processed and analyzed in real-time using advanced algorithms.",
  },
  {
    title: "Results",
    description:
      "Receive comprehensive results and insights from the analyzed sample.",
  },
]

export default function HowItWorks() {
  return (
    <section id='how-it-works' className='py-20 bg-gray-50'>
      <div className='container mx-auto px-4'>
        <h2 className='text-3xl font-bold text-center text-gray-900 mb-12'>
          How CellSight Works
        </h2>
        <div className='flex flex-col md:flex-row items-center'>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className='md:w-1/2 mb-10 md:mb-0'
          >
            <Image
              src='/image.jpg'
              alt='CellSight Process'
              width={600}
              height={400}
              className='rounded-lg shadow-lg'
            />
          </motion.div>
          <div className='md:w-1/2 md:pl-12'>
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className='mb-6'
              >
                <h3 className='text-xl font-semibold text-gray-900 mb-2'>
                  {index + 1}. {step.title}
                </h3>
                <p className='text-gray-600'>{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
