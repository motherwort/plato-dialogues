#!/bin/bash

echo "ENTERING..."

set -euo pipefail\

uvicorn src.main:app --host=0.0.0.0 --reload
