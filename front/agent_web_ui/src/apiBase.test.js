import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

import { resolveApiUrl, resolveProxyTarget } from './apiBase.js'

test('empty base stays on the current site', () => {
  assert.equal(resolveApiUrl('/api/query', ''), '/api/query')
  assert.equal(resolveApiUrl('/api/query', '   '), '/api/query')
  assert.equal(resolveApiUrl('/api/user_sessions', undefined), '/api/user_sessions')
})

test('absolute base joins the main API path once', () => {
  assert.equal(
    resolveApiUrl('/api/query', 'http://10.0.0.8:9000/'),
    'http://10.0.0.8:9000/api/query',
  )
  assert.equal(
    resolveApiUrl('api/user_sessions', 'http://10.0.0.8:9000'),
    'http://10.0.0.8:9000/api/user_sessions',
  )
})

test('proxy target defaults to the local main API and keeps a custom host', () => {
  assert.equal(resolveProxyTarget(undefined), 'http://127.0.0.1:8000')
  assert.equal(resolveProxyTarget(''), 'http://127.0.0.1:8000')
  assert.equal(resolveProxyTarget('http://192.168.1.20:18000/'), 'http://192.168.1.20:18000')
})

test('chat page no longer fetches a hardcoded host', () => {
  const source = readFileSync(new URL('./App.vue', import.meta.url), 'utf8')
  assert.equal(source.includes('127.0.0.1'), false)
  assert.match(source, /apiUrl\('\/api\/user_sessions'\)/)
  assert.match(source, /apiUrl\('\/api\/query'\)/)
})

test('vite reads the proxy target from the environment', () => {
  const source = readFileSync(new URL('../vite.config.js', import.meta.url), 'utf8')
  assert.match(source, /resolveProxyTarget\(process\.env\.API_PROXY_TARGET\)/)
  assert.equal(source.includes('127.0.0.1'), false)
})
