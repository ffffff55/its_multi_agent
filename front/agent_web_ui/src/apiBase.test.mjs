import assert from 'node:assert/strict'
import test from 'node:test'
import { resolveApiUrl } from './apiBase.js'

test('empty base stays relative so Vite can proxy', () => {
  assert.equal(resolveApiUrl('/api/query', ''), '/api/query')
  assert.equal(resolveApiUrl('/api/query', '   '), '/api/query')
  assert.equal(resolveApiUrl('api/user_sessions', undefined), '/api/user_sessions')
})

test('absolute base is joined without a double slash', () => {
  assert.equal(
    resolveApiUrl('/api/user_sessions', 'http://10.0.0.8:9000'),
    'http://10.0.0.8:9000/api/user_sessions',
  )
  assert.equal(
    resolveApiUrl('/api/query', 'http://10.0.0.8:9000/'),
    'http://10.0.0.8:9000/api/query',
  )
})
