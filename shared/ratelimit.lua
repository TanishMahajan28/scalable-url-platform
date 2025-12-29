-- Token Bucket Rate Limiter (atomic)
-- KEYS[1] = key for the client bucket
-- ARGV[1] = capacity (max tokens)
-- ARGV[2] = refill_rate (tokens per second)
-- ARGV[3] = now_ms (current time in milliseconds)
-- ARGV[4] = cost (tokens per request)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])

-- bucket state stored as: "tokens:last_ms"
local state = redis.call("GET", key)

local tokens = capacity
local last_ms = now_ms

if state then
  local sep = string.find(state, ":")
  if sep then
    tokens = tonumber(string.sub(state, 1, sep - 1))
    last_ms = tonumber(string.sub(state, sep + 1))
  end
end

-- Refill
local delta_ms = now_ms - last_ms
if delta_ms < 0 then delta_ms = 0 end

local refill = (delta_ms / 1000.0) * refill_rate
tokens = math.min(capacity, tokens + refill)

local allowed = 0
local remaining = tokens

if tokens >= cost then
  allowed = 1
  tokens = tokens - cost
  remaining = tokens
end

-- Persist state with TTL so Redis doesn't grow forever.
-- TTL: enough time for a full refill + buffer
local ttl_sec = math.ceil((capacity / refill_rate) * 2)
if ttl_sec < 1 then ttl_sec = 1 end

redis.call("SETEX", key, ttl_sec, tostring(tokens) .. ":" .. tostring(now_ms))

-- Compute retry-after seconds (roughly)
local retry_after = 0
if allowed == 0 then
  local needed = cost - tokens
  retry_after = math.ceil(needed / refill_rate)
end

return { allowed, remaining, retry_after }
