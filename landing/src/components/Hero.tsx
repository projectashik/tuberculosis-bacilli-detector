"use client"

import { motion } from "framer-motion"
import Image from "next/image"

export default function Hero() {
  return (
    <section className='bg-gray-50 py-20'>
      <div className='container mx-auto px-4 gap-5 flex flex-col md:flex-row items-center'>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className='md:w-1/2 mb-10 md:mb-0'
        >
          <h1 className='text-4xl md:text-5xl font-bold text-gray-900 mb-4'>
            Revolutionizing Microscopic Analysis with CellSight
          </h1>
          <p className='text-xl text-gray-600 mb-8'>
            Automated, accurate, and efficient microscopic sampling for the
            future of medical diagnostics.
          </p>
          <motion.a
            href='/about'
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className='bg-blue-600 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-blue-700 transition-colors duration-200'
          >
            Learn More
          </motion.a>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className='md:w-1/2'
        >
          <Image
            src='/landing-img.jpg'
            alt='Illustration of CellSight Device in use'
            width={600}
            height={400}
            className='rounded-lg shadow-lg'
          />
        </motion.div>
      </div>
    </section>
  )
}
