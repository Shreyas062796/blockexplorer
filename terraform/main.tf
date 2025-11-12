resource "google_cloud_run_service" "service" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        env {
          name  = "INFURA_ENDPOINT"
          value = "https://mainnet.infura.io/v3/f3c095656381439aa1acb1722d9c62f2"
        }
      }
    }
  }

  traffics {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated invocations (public)
resource "google_cloud_run_service_iam_member" "noauth" {
  service = google_cloud_run_service.service.name
  location = google_cloud_run_service.service.location
  role = "roles/run.invoker"
  member = "allUsers"
}
