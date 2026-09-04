import assert from 'node:assert/strict'
import test from 'node:test'
import { runTool } from './index.js'

const originalFetch = globalThis.fetch
test.afterEach(() => {
  globalThis.fetch = originalFetch
})

test('test test', async () => {
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        test: 'test',
      }),
    )
  const result = await runTool(undefined, { limit: 2 })
  console.log(result)
  assert.equal(2, 1, 'Big time error.')
})
