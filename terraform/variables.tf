variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "insuranceletters"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    project     = "insurance-letters"
    managed_by  = "terraform"
  }
}

# Azure OpenAI Configuration
variable "openai_deployment_name" {
  description = "Azure OpenAI deployment name"
  type        = string
}

variable "openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  type        = string
}

variable "openai_api_key" {
  description = "Azure OpenAI API key"
  type        = string
  sensitive   = true
}

variable "openai_api_version" {
  description = "Azure OpenAI API version"
  type        = string
  default     = "2024-02-15-preview"
}

# Azure AD Configuration
variable "azure_ad_tenant_id" {
  description = "Azure AD Tenant ID"
  type        = string
}

variable "azure_ad_client_id" {
  description = "Azure AD Application Client ID"
  type        = string
}

# Cosmos DB Configuration
variable "cosmos_database_name" {
  description = "Cosmos DB database name"
  type        = string
  default     = "insurance_letters"
}

# CORS Configuration
variable "additional_cors_origins" {
  description = "Additional CORS origins to allow"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

# API Management Configuration
variable "deploy_apim" {
  description = "Whether to deploy API Management"
  type        = bool
  default     = true
}

variable "apim_publisher_name" {
  description = "API Management publisher name"
  type        = string
  default     = "Insurance Letters Team"
}

variable "apim_publisher_email" {
  description = "API Management publisher email"
  type        = string
}