#!/usr/bin/env node
// Render every ```mermaid block in every Markdown file (and diagrams/src/*.mmd) with
// @mermaid-js/mermaid-cli to prove the syntax is valid. One browser for all diagrams.
// Usage: node scripts/validate/mermaid_check.mjs [file.md ...]
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer'
import { renderMermaid } from '@mermaid-js/mermaid-cli'

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
const EXCLUDE = new Set(['node_modules', '.git', '.site_src', 'site', '__pycache__'])

function walk (dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (EXCLUDE.has(e.name)) continue
    const p = path.join(dir, e.name)
    if (e.isDirectory()) walk(p, out)
    else if (e.name.endsWith('.md') || (e.name.endsWith('.mmd') && p.includes(path.join('diagrams', 'src')))) out.push(p)
  }
  return out
}

function blocks (file) {
  const text = fs.readFileSync(file, 'utf8')
  if (file.endsWith('.mmd')) return [{ line: 1, code: text }]
  const lines = text.split('\n')
  const out = []
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*```mermaid\s*$/.test(lines[i])) {
      const start = i + 1
      const body = []
      i++
      while (i < lines.length && !/^\s*```\s*$/.test(lines[i])) { body.push(lines[i]); i++ }
      out.push({ line: start, code: body.join('\n') })
    }
  }
  return out
}

const args = process.argv.slice(2)
const files = args.length ? args.map(a => path.resolve(a)) : walk(REPO)
const jobs = files.flatMap(f => blocks(f).map(b => ({ file: path.relative(REPO, f), ...b })))
if (!jobs.length) { console.log('mermaid_check: no mermaid blocks found'); process.exit(0) }

const launch = { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
const exe = process.env.PUPPETEER_EXECUTABLE_PATH || (fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined)
if (exe) launch.executablePath = exe
const browser = await puppeteer.launch(launch)
const failures = []
let ok = 0
try {
  for (const j of jobs) {
    try {
      const { data } = await renderMermaid(browser, j.code, 'svg', { backgroundColor: 'white' })
      const svg = Buffer.from(data).toString('utf8')
      if (/Syntax error in text|aria-roledescription="error"/.test(svg)) throw new Error('mermaid rendered an error diagram')
      ok++
    } catch (err) {
      failures.push(`${j.file}:${j.line}: ${String(err.message || err).split('\n').slice(0, 3).join(' | ')}`)
    }
  }
} finally {
  await browser.close()
}
if (failures.length) {
  console.log(`mermaid_check: ${failures.length} of ${jobs.length} diagrams failed to render`)
  for (const f of failures) console.log('  ✗ ' + f)
  process.exit(1)
}
console.log(`mermaid_check: OK (${ok} diagrams rendered)`)
