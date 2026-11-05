#!/usr/bin/env node
// Batch-render Mermaid definitions to SVG files with one browser (used by the PDF builder).
// Usage: node scripts/build/mermaid_render.mjs <jobs.json> <out_dir>
//   jobs.json = [{"id": "<hash>", "code": "<mermaid source>"}, ...]  -> <out_dir>/<id>.svg
import fs from 'node:fs'
import path from 'node:path'
import puppeteer from 'puppeteer'
import { renderMermaid } from '@mermaid-js/mermaid-cli'

const [jobsFile, outDir] = process.argv.slice(2)
const jobs = JSON.parse(fs.readFileSync(jobsFile, 'utf8'))
fs.mkdirSync(outDir, { recursive: true })
const launch = { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
const exe = process.env.PUPPETEER_EXECUTABLE_PATH || (fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined)
if (exe) launch.executablePath = exe
const font = '"Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans", sans-serif'
const mermaidConfig = {
  theme: 'neutral',
  fontFamily: font,
  themeVariables: { fontFamily: font, fontSize: '14px' },
  flowchart: { htmlLabels: false, useMaxWidth: false },
  sequence: { useMaxWidth: false },
  gantt: { useMaxWidth: false },
}
const browser = await puppeteer.launch(launch)
let ok = 0; const failed = []
try {
  for (const j of jobs) {
    const out = path.join(outDir, `${j.id}.svg`)
    if (fs.existsSync(out)) { ok++; continue }
    try {
      const { data } = await renderMermaid(browser, j.code, 'svg', { backgroundColor: 'white', mermaidConfig })
      fs.writeFileSync(out, Buffer.from(data))
      ok++
    } catch (e) { failed.push(j.id + ': ' + String(e.message || e).split('\n')[0]) }
  }
} finally { await browser.close() }
console.log(`mermaid_render: ${ok} rendered, ${failed.length} failed`)
for (const f of failed) console.log('  ✗ ' + f)
