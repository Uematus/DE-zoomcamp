terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.16.0"
    }
  }
}

provider "google" {
  credentials = "./keys/terr-creds.json"
  project     = "de-zoomcamp-484910"
  region      = "us-central1"
}