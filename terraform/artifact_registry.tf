resource "google_artifact_registry_repository" "service" {
  project       = var.project
  location      = var.artifact_registry_location
  repository_id = var.service_name
  description   = "Container images for ${var.service_name}"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }
}

