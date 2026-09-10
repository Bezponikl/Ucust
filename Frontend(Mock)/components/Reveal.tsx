"use client";

import { motion, type HTMLMotionProps } from "framer-motion";
import { fadeUp, viewportOnce } from "@/lib/motion";

type RevealProps = HTMLMotionProps<"div"> & {
  delay?: number;
};

export default function Reveal({ delay = 0, children, ...props }: RevealProps) {
  return (
    <motion.div
      variants={fadeUp}
      initial="hidden"
      whileInView="visible"
      viewport={viewportOnce}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1], delay }}
      {...props}
    >
      {children}
    </motion.div>
  );
}
