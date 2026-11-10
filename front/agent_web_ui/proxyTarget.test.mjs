import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { resolveProxyTarget } from './proxyTarget.js'

test('proxy target defaults to the local main API and trims a trailing slash', () => {
  assert.equal(resolveProxyTarget(undefined), 'http://127.0.0.1:8000')
  assert.equal(resolveProxyTarget(''), 'http://127.0.0.1:8000')
  assert.equal(resolveProxyTarget('   '), 'http://127.0.0.1:8000')
  assert.equal(resolveProxyTarget('http://192.168.1.20:18000/'), 'http://192.168.1.20:18000')
})

test('dev proxy target is not a VITE_ variable, so the page cannot see it', () => {
  const config = readFileSync(new URL('./vite.config.js', import.meta.url), 'utf8')
  const example = readFileSync(new URL('./.env.example', import.meta.url), 'utf8')
  const readme = readFileSync(new URL('../../README.md', import.meta.url), 'utf8')
  assert.match(config, /API_PROXY_TARGET/)
  assert.match(example, /^API_PROXY_TARGET=/m)
  assert.match(readme, /API_PROXY_TARGET=/)
  assert.equal(config.includes('VITE_DEV_PROXY_TARGET'), false)
  assert.equal(example.includes('VITE_DEV_PROXY_TARGET'), false)
  assert.equal(readme.includes('VITE_DEV_PROXY_TARGET'), false)
})

test('chat page does not hardcode the main API host', () => {
  const source = readFileSync(new URL('./src/App.vue', import.meta.url), 'utf8')
  const clientApi = readFileSync(new URL('./src/apiBase.js', import.meta.url), 'utf8')
  assert.equal(source.includes('127.0.0.1'), false)
  assert.equal(clientApi.includes('127.0.0.1'), false)
  assert.match(source, /apiUrl\('\/api\/user_sessions'\)/)
  assert.match(source, /apiUrl\('\/api\/query'\)/)
})
