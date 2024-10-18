terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "4.5.0"
    }
    }
     backend "azurerm" {
      resource_group_name  = "kp-rg"
      storage_account_name = "githubactionstr"
      container_name       = "cariadcnt"
      key                  = "cariad.tfstate"
  }
}
provider "azurerm" {
  features {}
}
