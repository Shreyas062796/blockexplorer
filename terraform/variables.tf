variable "project" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "service_name" {
  type    = string
  default = "eth-balance-service"
}

variable "image" {
  type    = string
  default = "" # e.g. gcr.io/<PROJECT>/eth-balance:latest
}

variable "state_bucket_name" {
  type = string
}

variable "state_bucket_location" {
  type    = string
  default = "US"
}

variable "artifact_registry_location" {
  type    = string
  default = "us-central1"
}
