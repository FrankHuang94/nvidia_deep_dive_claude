#!/usr/bin/env node
// Print an HTML file to an A4 PDF with Chromium (Playwright). Used by zh_pdf.py.
// Usage: node scripts/build/print_pdf.cjs <in.html> <out.pdf> "<running header text>"
const { chromium } = require('playwright')
;(async () => {
  const [html, pdf, title] = process.argv.slice(2)
  const browser = await chromium.launch()
  const page = await browser.newPage()
  await page.goto('file://' + html, { waitUntil: 'load', timeout: 0 })
  await page.evaluate(async () => { await document.fonts.ready })
  const font = "font-family:'Noto Sans CJK SC','WenQuanYi Zen Hei',sans-serif;"
  await page.pdf({
    path: pdf, format: 'A4', printBackground: true, displayHeaderFooter: true, outline: true, tagged: true,
    headerTemplate: `<div style="${font}font-size:7pt;color:#8a8a8a;width:100%;padding:0 17mm;text-align:right;">${title}</div>`,
    footerTemplate: `<div style="${font}font-size:7.5pt;color:#8a8a8a;width:100%;text-align:center;">— <span class="pageNumber"></span> —</div>`,
    margin: { top: '17mm', bottom: '15mm', left: '17mm', right: '17mm' },
  })
  await browser.close()
})().catch(e => { console.error(e); process.exit(1) })
