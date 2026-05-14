const BASE = '/api'

async function handleResponse(res) {
  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      message = body.error || body.message || message
    } catch { /* ignore */ }
    throw new Error(message)
  }
  return res.json()
}

export async function getConversations() {
  const res = await fetch(`${BASE}/conversations`)
  return handleResponse(res)
}

export async function createConversation(provider = 'anthropic') {
  const res = await fetch(`${BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider }),
  })
  return handleResponse(res)
}

export async function getConversation(id) {
  const res = await fetch(`${BASE}/conversations/${id}`)
  return handleResponse(res)
}

export async function updateConversation(id, data) {
  const res = await fetch(`${BASE}/conversations/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return handleResponse(res)
}

export async function deleteConversation(id) {
  const res = await fetch(`${BASE}/conversations/${id}`, {
    method: 'DELETE',
  })
  return handleResponse(res)
}

/**
 * Returns the raw fetch Response for SSE streaming.
 * Caller is responsible for reading the body as a stream.
 */
export async function sendMessage(conversationId, message, provider = 'anthropic') {
  const res = await fetch(`${BASE}/chat/${conversationId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ message, provider }),
  })

  if (!res.ok) {
    let errMsg = `HTTP ${res.status}`
    try {
      const body = await res.json()
      errMsg = body.error || errMsg
    } catch { /* ignore */ }
    throw new Error(errMsg)
  }

  return res
}
