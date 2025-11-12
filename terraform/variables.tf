variable "project" {
  type = string
  default = "blockexplorer-478015"
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
  default = "" # e.g. us-central1-docker.pkg.dev/<PROJECT>/eth-balance-service/eth-balance-service:<tag>
}

variable "state_bucket_name" {
  type    = string
  default = ""
}

variable "state_bucket_location" {
  type    = string
  default = "US"
}

variable "artifact_registry_location" {
  type    = string
  default = "us-central1"
}
