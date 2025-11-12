resource "google_storage_bucket" "terraform_state" {
  name          = var.state_bucket_name
  location      = var.state_bucket_location
  project       = var.project
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 180
    }
  }
}

