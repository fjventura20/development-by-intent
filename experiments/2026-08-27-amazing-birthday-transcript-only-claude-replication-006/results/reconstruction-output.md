# reconstruction — v0.2 freeze-discipline captured from reconstruction-raw.json

## Envelope metadata
```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "api_error_status": null,
  "duration_ms": 4939,
  "duration_api_ms": 5931,
  "ttft_ms": 4924,
  "ttft_stream_ms": 2699,
  "time_to_request_ms": 51,
  "num_turns": 1,
  "stop_reason": "end_turn",
  "session_id": "19921118-022e-41a6-8323-910103401170",
  "total_cost_usd": 0.05868075,
  "usage": {
    "input_tokens": 3,
    "cache_creation_input_tokens": 14277,
    "cache_read_input_tokens": 11370,
    "output_tokens": 81,
    "server_tool_use": {
      "web_search_requests": 0,
      "web_fetch_requests": 0
    },
    "service_tier": "standard",
    "cache_creation": {
      "ephemeral_1h_input_tokens": 14277,
      "ephemeral_5m_input_tokens": 0
    },
    "inference_geo": "not_available",
    "iterations": [
      {
        "input_tokens": 3,
        "output_tokens": 81,
        "cache_read_input_tokens": 11370,
        "cache_creation_input_tokens": 14277,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 0,
          "ephemeral_1h_input_tokens": 14277
        },
        "type": "message"
      }
    ],
    "speed": "standard"
  },
  "modelUsage": {
    "claude-haiku-4-5-20251001": {
      "inputTokens": 442,
      "outputTokens": 13,
      "cacheReadInputTokens": 0,
      "cacheCreationInputTokens": 0,
      "webSearchRequests": 0,
      "costUSD": 0.000507,
      "contextWindow": 200000,
      "maxOutputTokens": 32000
    },
    "claude-sonnet-4-6": {
      "inputTokens": 3,
      "outputTokens": 81,
      "cacheReadInputTokens": 11370,
      "cacheCreationInputTokens": 14277,
      "webSearchRequests": 0,
      "costUSD": 0.058173749999999996,
      "contextWindow": 200000,
      "maxOutputTokens": 32000
    }
  },
  "permission_denials": [],
  "terminal_reason": "completed",
  "fast_mode_state": "off",
  "uuid": "d9927b3d-96d2-4a8f-9f80-f761e107bfda"
}
```

## Result text (first-call raw, no repair)

READY — I am an "Amazing Birthday" storytelling artifact that takes a birth date as input (triggered by "Birthdate [date]") and produces a selective, narrative-style report highlighting 5–10 surprising historical connections from that exact date, woven into the arc of a person's lifetime, written in an engaging essay format rather than a chronological list.

