#!/usr/bin/env tsx
/**
 * Validates tesla-tracking-data.json against the Zod schema
 * Exits with code 1 if validation fails
 * Used in CI/CD to prevent deploying invalid data
 */

import { readFileSync } from 'fs'
import { validateTeslaData, validateDataInvariants } from '../src/schema'

const data = JSON.parse(readFileSync('tesla-tracking-data.json', 'utf-8'))

console.log('======================================================================')
console.log('Validating data against Zod schema (Frontend validation)')
console.log('======================================================================\n')

const result = validateTeslaData(data)

if (!result.success) {
  console.error('❌ Schema validation failed:\n')
  result.errors.forEach(err => console.error(`  - ${err}`))
  console.error('\n======================================================================')
  console.error('❌ VALIDATION FAILED - Fix schema errors before deploying')
  console.error('======================================================================')
  process.exit(1)
}

console.log('✅ Schema validation passed')

const invariantErrors = validateDataInvariants(result.data)
if (invariantErrors.length > 0) {
  console.warn('\n⚠️  Data invariant warnings:')
  invariantErrors.forEach(err => console.warn(`  - ${err}`))
  console.warn('\n⚠️  These are warnings only - deployment will continue')
}

console.log('\n======================================================================')
console.log('✅ Zod schema validation complete')
console.log('======================================================================')
