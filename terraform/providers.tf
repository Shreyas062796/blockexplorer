terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
  # Backend is configured via CLI in CI/CD with -backend-config flags
  # For local development, use: terraform init -migrate-state -backend=false
  # Then: terraform init -backend-config="bucket=..." -backend-config="prefix=..."
  backend "gcs" {
    # bucket and prefix are provided via -backend-config in CI/CD
  }
}

provider "google" {
  project = var.project
  region  = var.region
}
