# CloudOps Dashboard - DevSecOps Security Policy

## Purpose

This application demonstrates a secure CI/CD pipeline for a healthcare cloud environment.

## Security Controls

### 1. Source Code Security
- Application source code must be tested before deployment.
- Sensitive credentials must not be stored in source code.
- Code changes must be tracked using Git.

### 2. Dependency Security
- Python dependencies must be scanned for known vulnerabilities.
- Vulnerable dependencies should be identified before deployment.

### 3. Container Security
- Docker images must be scanned for known vulnerabilities.
- Images with critical security vulnerabilities must not be deployed.

### 4. Application Security
- The application must expose a health endpoint.
- Application containers should run with minimum required privileges.
- Debug mode must not be enabled in production.

### 5. Kubernetes Security
- Kubernetes workloads should use resource limits.
- Health probes must be configured.
- Production traffic should only be routed to healthy pods.

### 6. Deployment Security
- Security checks must execute before deployment.
- A failed security check must stop the pipeline.
- Deployment should only proceed after security validation.

## Healthcare Security Goal

The DevSecOps pipeline helps protect healthcare applications by detecting security problems early in the software delivery lifecycle.
