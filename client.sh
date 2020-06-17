#!/bin/bash

API_KEY=your-api-key
API_SECRET=your-api-secret

curl --data "{\"api_key\": \"${API_KEY}\", \"api_secret\": \"${API_SECRET}\"}" \
    http://localhost:5000/ \
    --header "Content-Type:application/json" \
    --http1.1
