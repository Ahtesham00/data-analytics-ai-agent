/**
 * Parses a Server-Sent Events stream from a fetch Response.
 * Yields { event, data } objects as they arrive.
 * SSE messages are separated by blank lines (\n\n).
 */
export async function* parseSSEStream(response) {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // SSE messages are separated by double newlines
      const parts = buffer.split('\n\n')
      buffer = parts.pop() ?? ''

      for (const part of parts) {
        const trimmed = part.trim()
        if (!trimmed) continue

        const lines = trimmed.split('\n')
        let eventType = 'message'
        let dataStr = ''

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            dataStr = line.slice(6).trim()
          }
        }

        if (dataStr) {
          try {
            yield { event: eventType, data: JSON.parse(dataStr) }
          } catch {
            // skip malformed data
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
