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

const declaredTracks = new Set(Object.keys(isRecord(manifest.frames2d?.tracks) ? manifest.frames2d.tracks : {}))
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

  const gameplay = manifest.gameplay
  if (gameplay !== undefined) {
    if (!isRecord(gameplay)) {
      error('gameplay must be an object')
    } else {
      const stats = new Set()
      if (gameplay.stats !== undefined) {
        if (!isRecord(gameplay.stats)) error('gameplay.stats must be an object')
        else {
          for (const [name, def] of Object.entries(gameplay.stats)) {
            stats.add(name)
            if (!isRecord(def)) {
              error(`gameplay.stats.${name} must be an object`)
              continue
            }
            if (!Number.isInteger(def.max) || def.max < 1 || def.max > 1_000_000) {
              error(`gameplay.stats.${name}.max must be an integer in [1, 1000000]`)
            }
            if (def.initial !== undefined && (typeof def.initial !== 'number' || def.initial < 0 || def.initial > def.max)) {
              error(`gameplay.stats.${name}.initial must be within [0, max]`)
            }
            for (const key of ['decayPerMinute', 'workingDecayPerMinute', 'idleDecayPerMinute']) {
              if (def[key] !== undefined && (typeof def[key] !== 'number' || def[key] < 0 || def[key] > 1000)) {
                error(`gameplay.stats.${name}.${key} must be a number in [0, 1000]`)
              }
            }
          }
        }
      }

      const checkEffects = (value, field) => {
        if (value === undefined) return
        if (!Array.isArray(value)) {
          error(`${field} must be an array`)
          return
        }
        for (const [index, effect] of value.entries()) {
          if (!isRecord(effect)) {
            error(`${field}[${index}] must be an object`)
            continue
          }
          if (typeof effect.amount !== 'number' || !Number.isFinite(effect.amount)) {
            error(`${field}[${index}].amount must be a finite number`)
          }
          if (effect.stat !== undefined && (typeof effect.stat !== 'string' || !stats.has(effect.stat))) {
            error(`${field}[${index}] references an undeclared stat: ${JSON.stringify(effect.stat)}`)
          }
          if (effect.currency !== undefined && typeof effect.currency !== 'string') {
            error(`${field}[${index}].currency must be a string`)
          }
        }
      }

      const director = gameplay.idleDirector
      if (director !== undefined) {
        if (!isRecord(director) || !Array.isArray(director.acts)) {
          error('gameplay.idleDirector must be an object with an acts array')
        } else {
          if (!Number.isInteger(director.intervalMs) || director.intervalMs < 1000 || director.intervalMs > 60_000) {
            error('gameplay.idleDirector.intervalMs must be an integer in [1000, 60000]')
          }
          if (!Number.isInteger(director.maxMiss) || director.maxMiss < 0 || director.maxMiss > 10) {
            error('gameplay.idleDirector.maxMiss must be an integer in [0, 10]')
          }
          if (!Number.isInteger(director.idleWeight) || director.idleWeight < 0 || director.idleWeight > 10_000) {
            error('gameplay.idleDirector.idleWeight must be an integer in [0, 10000]')
          }
          if (director.acts.length === 0 || director.acts.length > 16) {
            error('gameplay.idleDirector.acts must declare 1..16 acts')
          }
          for (const [index, act] of director.acts.entries()) {
            if (!isRecord(act)) {
              error(`gameplay.idleDirector.acts[${index}] must be an object`)
              continue
            }
            if (typeof act.track !== 'string' || !declaredTracks.has(act.track)) {
              error(`gameplay.idleDirector.acts[${index}] references an undeclared track: ${JSON.stringify(act.track)}`)
            }
            if (!Number.isInteger(act.weight) || act.weight < 1 || act.weight > 10_000) {
              error(`gameplay.idleDirector.acts[${index}].weight must be an integer in [1, 10000]`)
            }
          }
        }
      }

      const box = gameplay.hitBox
      if (box !== undefined) {
        if (!isRecord(box)
          || ![box.x0, box.x1, box.y0, box.y1].every(value => typeof value === 'number' && value >= 0 && value <= 1)
          || !(box.x0 < box.x1) || !(box.y0 < box.y1)) {
          error('gameplay.hitBox must be { x0, y0, x1, y1 } fractions with x0 < x1 and y0 < y1')
        }
      }

      const touch = gameplay.touch
      if (touch !== undefined) {
        if (!isRecord(touch) || !Array.isArray(touch.zones)) {
          error('gameplay.touch must be an object with a zones array')
        } else {
          if (touch.zones.length === 0 || touch.zones.length > 8) {
            error('gameplay.touch.zones must declare 1..8 zones')
          }
          for (const [index, zone] of touch.zones.entries()) {
            if (!isRecord(zone) || typeof zone.name !== 'string' || !TRACK_PATTERN.test(zone.name)
              || typeof zone.y0 !== 'number' || typeof zone.y1 !== 'number'
              || zone.y0 < 0 || zone.y1 > 1 || !(zone.y0 < zone.y1)) {
              error(`gameplay.touch.zones[${index}] needs a kebab name and 0 <= y0 < y1 <= 1`)
              continue
            }
            if (!Array.isArray(zone.branches) || zone.branches.length === 0 || zone.branches.length > 8) {
              error(`gameplay.touch.zones[${index}].branches must declare 1..8 branches`)
              continue
            }
            let probabilitySum = 0
            for (const [branchIndex, branch] of zone.branches.entries()) {
              if (!isRecord(branch) || typeof branch.probability !== 'number'
                || branch.probability <= 0 || branch.probability > 1) {
                error(`gameplay.touch.zones[${index}].branches[${branchIndex}].probability must be in (0, 1]`)
                continue
              }
              probabilitySum += branch.probability
              if (branch.state !== undefined && (typeof branch.state !== 'string' || !declaredTracks.has(branch.state))) {
                error(`gameplay.touch.zones[${index}].branches[${branchIndex}] references an undeclared track: ${JSON.stringify(branch.state)}`)
              }
              if (branch.stateMs !== undefined && (!Number.isInteger(branch.stateMs) || branch.stateMs < 200 || branch.stateMs > 10_000)) {
                error(`gameplay.touch.zones[${index}].branches[${branchIndex}].stateMs must be an integer in [200, 10000]`)
              }
              checkEffects(branch.effects, `gameplay.touch.zones[${index}].branches[${branchIndex}].effects`)
            }
            if (probabilitySum > 1 + 1e-9) {
              error(`gameplay.touch.zones[${index}].branches probabilities must sum to at most 1`)
            }
          }
        }
      }

      console.log(`gameplay: ${stats.size} stats, ${director?.acts?.length ?? 0} idle acts, ${touch?.zones?.length ?? 0} touch zones`)
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
