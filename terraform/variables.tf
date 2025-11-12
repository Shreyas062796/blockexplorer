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
