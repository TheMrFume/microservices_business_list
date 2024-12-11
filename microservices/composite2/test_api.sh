#!/bin/bash

# Test the view_full_list endpoint
curl -X GET "http://127.0.0.1:8003/composite/view_full_list?list_id=1" \
     -H "X-Token: {\"user_token\":\"sample_token\",\"user_id\":\"1234\"}" \
     -H "X-Correlation-ID: test-correlation-id"

# Test the serve_next endpoint
curl -X GET "http://127.0.0.1:8003/composite/serve_next?list_id=1&location=NYC" \
     -H "X-Token: {\"user_token\":\"sample_token\",\"user_id\":\"1234\"}" \
     -H "X-Correlation-ID: test-correlation-id"