"use client";

import { motion } from "framer-motion";
import { Zap, DollarSign, MapPin, Layers } from "lucide-react";

const benefits = [
  {
    icon: Layers,
    title: "Multiple Tests, One Device",
    description:
      "A single CellSight device can run multiple microscopic screening tests, saving space and resources.",
  },
  {
    icon: Zap,
    title: "Easy to Use",
    description:
      "User-friendly interface and automated processes make CellSight simple to operate for all skill levels.",
  },
  {
    icon: MapPin,
    title: "Remote Access",
    description:
      "CellSight can be deployed and operated in remote areas, bringing advanced diagnostics to underserved regions.",
  },
  {
    icon: DollarSign,
    title: "Cost-Effective",
    description:
      "Affordable pricing and multi-functionality make CellSight a cost-effective solution for healthcare providers.",
  },
];

export default function Benefits() {
  return (
    <section id="benefits" className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <h2 className="section-title">Why Choose CellSight?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex items-start space-x-4"
            >
              <div className="flex-shrink-0">
                <benefit.icon className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-primary mb-2">
                  {benefit.title}
                </h3>
                <p className="text-text">{benefit.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
