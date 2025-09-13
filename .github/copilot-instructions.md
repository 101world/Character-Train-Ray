# Copilot Instructions for FluxGym RunPod Serverless

## Project Overview
This project creates a RunPod serverless endpoint for FLUX LoRA training using FluxGym integration.

## Reference Repositories
- FluxGym: https://github.com/cocktailpeanut/fluxgym
- RunPod Serverless: https://github.com/runpod/serverless-workers

## Development Checklist

### Phase 1: Project Scaffolding ✅
- [x] Create .github/copilot-instructions.md file with project setup guidelines
- [x] Clarify project requirements: RunPod serverless endpoint for FLUX LoRA training using FluxGym
- [ ] Get project setup info and create basic project structure for RunPod serverless endpoint

### Phase 2: Project Customization
- [ ] Implement FluxGym integration and FLUX LoRA training functionality  
- [ ] Install any necessary VS Code extensions for development

### Phase 3: Project Compilation  
- [ ] Install dependencies and resolve any compilation issues

### Phase 4: Project Launch
- [ ] Create VS Code tasks for building and running the endpoint
- [ ] Test the endpoint locally if possible
- [ ] Ensure README.md and documentation are complete and accurate

## Technical Requirements
- Python-based RunPod serverless handler
- FluxGym integration for FLUX LoRA training
- Cloudflare R2 storage support (existing credentials available)
- Docker containerization for RunPod deployment
- Proper error handling and logging

## Previous Issues to Avoid
- Container startup failures ("exec python failed")
- NumPy compatibility issues (use numpy==1.24.3)
- Missing RunPod serverless startup code
- 2-hour rebuild cycles due to configuration errors

## Success Criteria
- Functional FLUX LoRA training endpoint
- Proper FluxGym integration
- Stable RunPod serverless architecture
- Clean container builds
- Working test cases
