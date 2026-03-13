export function stripHtml(html: string): string {
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim()
}

export function getFirstSentence(html: string): string {
  const plainText = stripHtml(html)
  if (!plainText) return '暂无摘要'

  const parts = plainText.split(/(?<=[。！？.!?])/)
  const sentence = parts.find((item) => item.trim())?.trim() || plainText
  return sentence.slice(0, 140)
}