"use client";

import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import { Quote } from "lucide-react";
import Image from "next/image";

interface Testimonial {
  name: string;
  role: string;
  image: string;
  quote: string;
}

const testimonials: Testimonial[] = [
  {
    name: "Dr. Sarah Johnson",
    role: "Chief Pathologist",
    image: "/placeholder.svg",
    quote:
      "CellSight has revolutionized our lab's efficiency. We can now process samples faster and with greater accuracy than ever before.",
  },
  {
    name: "Dr. Michael Chen",
    role: "Rural Health Specialist",
    image: "/placeholder.svg",
    quote:
      "The portability and ease of use of CellSight have allowed us to bring advanced diagnostics to remote areas, significantly improving patient care.",
  },
  {
    name: "Prof. Emily Rodriguez",
    role: "Medical Research Director",
    image: "/placeholder.svg",
    quote:
      "The data collected by CellSight has been invaluable for our research. Its consistency and detail have accelerated our studies tremendously.",
  },
];

export default function Testimonials(): JSX.Element {
  return (
    <section className="py-20 bg-gradient-to-b from-primary/5 to-background">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl font-bold text-primary mb-4">
            What Experts Say
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Hear from healthcare professionals who have experienced the benefits
            of CellSight in their practice.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full backdrop-blur-sm bg-card/50 hover:bg-card/80 transition-all duration-300 hover:shadow-lg">
                <CardContent className="p-6">
                  <Quote className="w-8 h-8 text-primary/40 mb-4" />
                  <p className="text-foreground italic mb-6">
                    {testimonial.quote}
                  </p>
                  <div className="flex items-center">
                    <Image
                      src={testimonial.image}
                      alt={`Photo of ${testimonial.name}`}
                      width={48}
                      height={48}
                      className="rounded-full mr-4"
                      loading="lazy"
                    />
                    <div>
                      <h3 className="text-primary font-semibold">
                        {testimonial.name}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
