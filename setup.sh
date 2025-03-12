#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
echo "I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml" | pip install git+https://github.com/coqui-ai/TTS.git
