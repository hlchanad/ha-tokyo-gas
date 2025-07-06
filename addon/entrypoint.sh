#!/bin/sh
# Pass all environment variables to the Node.js process
exec env node /app/dist/index.js
