"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { useState } from "react"

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <header className='bg-white shadow-sm sticky top-0'>
      <nav className='container mx-auto px-4 py-4 flex justify-between items-center'>
        <Link href='/' className='text-2xl font-bold text-blue-600'>
          CellSight
        </Link>
        <div className='hidden md:flex space-x-6'>
          <NavLink href='#features'>Features</NavLink>
          <NavLink href='#how-it-works'>How It Works</NavLink>
          <NavLink href='#contact'>Contact</NavLink>
        </div>
        <div className='md:hidden'>
          <button onClick={() => setIsOpen(!isOpen)} aria-label='Toggle menu'>
            <svg
              className='w-6 h-6'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M4 6h16M4 12h16M4 18h16'
              />
            </svg>
          </button>
        </div>
      </nav>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className='md:hidden bg-white shadow-md py-2'
        >
          <div className='container mx-auto px-4 flex flex-col space-y-2'>
            <NavLink href='#features' onClick={() => setIsOpen(false)}>
              Features
            </NavLink>
            <NavLink href='#how-it-works' onClick={() => setIsOpen(false)}>
              How It Works
            </NavLink>
            <NavLink href='#contact' onClick={() => setIsOpen(false)}>
              Contact
            </NavLink>
          </div>
        </motion.div>
      )}
    </header>
  )
}

function NavLink({
  href,
  children,
  onClick,
}: {
  href: string
  children: React.ReactNode
  onClick?: () => void
}) {
  return (
    <Link
      href={href}
      className='text-gray-600 hover:text-blue-600 transition-colors duration-200'
      onClick={onClick}
    >
      {children}
    </Link>
  )
}
