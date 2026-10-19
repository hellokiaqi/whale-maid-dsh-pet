#!/usr/bin/env node
/**
 * Validate the pet package without importing the dsh-pet plugin internals.
 *
 * Checks the manifest-v2 structure we rely on (frames2d), that every declared
 * frame exists on disk, that durations line up, and that every phase/fallback
 * points at a declared track. Run it after editing pet.json or replacing frames.
 *
 * Usage: node scripts/verify.mjs
 */
import { existsSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const petDir = fileURLToPath(new URL('../pet/', import.meta.url))
const manifestPath = join(petDir, 'pet.json')
const errors = []
const warnings = []
const error = (message) => errors.push(message)
const warning = (message) => warnings.push(message)

const ID_PATTERN = /^[a-z0-9][a-z0-9-]*$/
const TRACK_PATTERN = /^[a-z0-9][a-z0-9-]*$/
const IMAGE_EXT = /\.(webp|png|gif|jpe?g)$/i
const PHASES = new Set(['idle', 'waiting', 'thinking', 'tool', 'review', 'done', 'failed'])
const MIN_MS = 16
const MAX_MS = 5000

function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

let manifest
try {
  manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
} catch (cause) {
  console.error(`cannot read ${manifestPath}: ${cause.message}`)
  process.exit(1)
}

if (!isRecord(manifest)) error('pet.json root must be an object')
if (manifest.petManifestVersion !== 2) error('petManifestVersion must be 2')
if (typeof manifest.id !== 'string' || !ID_PATTERN.test(manifest.id)) error('id must be a lowercase kebab id')
if (typeof manifest.displayName !== 'string' || manifest.displayName.trim() === '') error('displayName is required')
if (typeof manifest.license !== 'string' || manifest.license.trim() === '') error('license is required')
if (manifest.renderer !== 'frames2d') error('renderer must be "frames2d" for this package')

const block = manifest.frames2d
if (!isRecord(block)) {
  error('frames2d block is required')
} else {
  const tracks = isRecord(block.tracks) ? block.tracks : undefined
  if (tracks === undefined) error('frames2d.tracks must be an object')
  const trackNames = new Set(Object.keys(tracks ?? {}))
  if (trackNames.size === 0) error('frames2d.tracks must declare at least one track')
  if (trackNames.size > 64) error('frames2d.tracks may declare at most 64 tracks')

  const frameTotal = { count: 0, bytes: 0 }
  for (const [name, track] of Object.entries(tracks ?? {})) {
    if (!TRACK_PATTERN.test(name) || name.length > 32) error(`track ${JSON.stringify(name)} is not a lowercase kebab name (max 32)`)
    if (!isRecord(track)) {
      error(`track ${name} must be an object`)
      continue
    }
    if (!Array.isArray(track.frames) || track.frames.length === 0) {
      error(`track ${name}.frames must be a non-empty array`)
    } else if (track.frames.length > 64) {
      error(`track ${name}.frames may declare at most 64 frames`)
    }
    if (!Array.isArray(track.frameMs) || track.frameMs.length !== (track.frames?.length ?? 0)) {
      error(`track ${name}.frameMs must be an array with one value per frame`)
    } else {
      for (const ms of track.frameMs) {
        if (!Number.isInteger(ms) || ms < MIN_MS || ms > MAX_MS) {
          error(`track ${name}.frameMs values must be integers in [${MIN_MS}, ${MAX_MS}]`)
          break
        }
      }
    }
    if (track.loop !== undefined && typeof track.loop !== 'boolean') error(`track ${name}.loop must be a boolean`)
    if (track.fallback !== undefined && (typeof track.fallback !== 'string' || !trackNames.has(track.fallback))) {
      error(`track ${name}.fallback must name a declared track`)
    }
    for (const frame of track.frames ?? []) {
      if (typeof frame !== 'string' || frame === '' || frame.includes('/') || frame.includes('\\') || !IMAGE_EXT.test(frame)) {
        error(`track ${name} has an invalid frame name: ${JSON.stringify(frame)}`)
        continue
      }
      const file = join(petDir, name, frame)
      if (!existsSync(file)) {
        error(`missing frame: ${name}/${frame}`)
        continue
      }
      const stat = statSync(file)
      if (!stat.isFile() || stat.size === 0) error(`empty frame: ${name}/${frame}`)
      else {
        frameTotal.count += 1
        frameTotal.bytes += stat.size
      }
    }
  }

  const phases = isRecord(block.phases) ? block.phases : undefined
  if (phases === undefined || typeof phases.idle !== 'string') {
    error('frames2d.phases must declare an idle mapping')
  } else {
    for (const [phase, target] of Object.entries(phases)) {
      if (!PHASES.has(phase)) error(`unknown phase ${JSON.stringify(phase)}`)
      if (typeof target !== 'string' || !trackNames.has(target)) {
        error(`phase ${phase} maps to an undeclared track: ${JSON.stringify(target)}`)
      }
    }
    if (phases.done !== undefined && !trackNames.has(phases.done)) {
      error('phases.done must name a declared track')
    }
  }

  console.log(`pet:      ${manifest.id}  (${manifest.displayName})`)
  console.log(`tracks:   ${[...trackNames].join(', ')}`)
  console.log(`frames:   ${frameTotal.count} files, ${(frameTotal.bytes / 1024 / 1024).toFixed(2)} MB`)
  console.log(`phases:   ${JSON.stringify(block.phases)}`)
}

for (const message of warnings) console.warn(`warning: ${message}`)
if (errors.length > 0) {
  console.error(`\nFAILED (${errors.length}):`)
  for (const message of errors) console.error(`  - ${message}`)
  process.exit(1)
}
console.log('\nOK')
