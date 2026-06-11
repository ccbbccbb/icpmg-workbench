/**
 * Tailwind CSS class name utility.
 * Combines clsx for conditional classes with tailwind-merge for deduplication.
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges class names with Tailwind CSS conflict resolution.
 * Uses clsx for conditional class handling and tailwind-merge for deduplication.
 * @param inputs - Class values to merge (strings, arrays, objects)
 * @returns Merged and deduplicated class string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
