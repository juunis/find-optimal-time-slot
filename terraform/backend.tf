terraform {
  backend "s3" {
      bucket         = "find-optimal-time-slot-tfstate"
      key            = "terraform.tfstate"
      region         = "eu-west-1"
      encrypt        = true
  }
}
