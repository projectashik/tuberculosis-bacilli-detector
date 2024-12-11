import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { motion } from "framer-motion"
import { Check } from "lucide-react"

type TestName = "Malaria Detection" | "Tuberculosis Screening"

const availableTests: TestName[] = [
  "Malaria Detection",
  "Tuberculosis Screening",
]

export default function AvailableTests(): JSX.Element {
  return (
    <section id='available-tests' className='py-20 bg-primary/5'>
      <div className='container mx-auto px-4'>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className='text-center mb-12'
        >
          <h2 className='text-3xl font-bold text-primary mb-4'>
            Available Tests
          </h2>
          <p className='text-muted-foreground max-w-2xl mx-auto'>
            Our advanced microscopy system supports multiple diagnostic tests,
            with more being added regularly.
          </p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <Card className='max-w-2xl mx-auto backdrop-blur-sm bg-card/50'>
            <CardHeader>
              <CardTitle className='text-primary'>Current Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className='space-y-4'>
                {availableTests.map((test, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className='flex items-center space-x-3 p-3 rounded-lg hover:bg-primary/5 transition-colors'
                  >
                    <Check className='text-primary h-5 w-5' />
                    <span className='text-foreground'>{test}</span>
                  </motion.li>
                ))}
              </ul>
              <div className='mt-6 p-4 bg-secondary/10 rounded-lg'>
                <p className='text-center text-muted-foreground'>
                  More tests coming soon! Our team is constantly working on
                  expanding our capabilities.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
