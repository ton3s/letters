# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
  tags     = var.tags
}

# Storage Account for Function App
resource "azurerm_storage_account" "functions" {
  name                     = "${var.project_name}${var.environment}st"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = var.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "${var.project_name}-${var.environment}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  tags                = var.tags
}

# App Service Plan for Function App (Consumption Plan)
resource "azurerm_service_plan" "main" {
  name                = "${var.project_name}-${var.environment}-asp"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "Y1"
  tags                = var.tags
}

# Function App
resource "azurerm_linux_function_app" "main" {
  name                = "${var.project_name}-${var.environment}-func"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key
  service_plan_id            = azurerm_service_plan.main.id
  tags                       = var.tags

  site_config {
    application_insights_key               = azurerm_application_insights.main.instrumentation_key
    application_insights_connection_string = azurerm_application_insights.main.connection_string
    
    application_stack {
      python_version = "3.9"
    }

    cors {
      allowed_origins = concat(
        ["https://${azurerm_static_site.frontend.default_host_name}"],
        var.additional_cors_origins
      )
      support_credentials = true
    }
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsStorage"           = azurerm_storage_account.functions.primary_connection_string
    "AZURE_OPENAI_DEPLOYMENT_NAME"  = var.openai_deployment_name
    "AZURE_OPENAI_ENDPOINT"         = var.openai_endpoint
    "AZURE_OPENAI_API_KEY"          = var.openai_api_key
    "AZURE_OPENAI_API_VERSION"      = var.openai_api_version
    "COSMOS_DB_ENDPOINT"            = azurerm_cosmosdb_account.main.endpoint
    "COSMOS_DB_KEY"                 = azurerm_cosmosdb_account.main.primary_key
    "COSMOS_DB_DATABASE_NAME"       = azurerm_cosmosdb_sql_database.main.name
    "COSMOS_DB_CONTAINER_NAME"      = azurerm_cosmosdb_sql_container.letters.name
    "AZURE_AD_TENANT_ID"            = var.azure_ad_tenant_id
    "AZURE_AD_CLIENT_ID"            = var.azure_ad_client_id
  }

  identity {
    type = "SystemAssigned"
  }
}

# Cosmos DB Account (Serverless)
resource "azurerm_cosmosdb_account" "main" {
  name                = "${var.project_name}-${var.environment}-cosmos"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  
  capabilities {
    name = "EnableServerless"
  }

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }

  tags = var.tags
}

# Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.cosmos_database_name
  resource_group_name = azurerm_cosmosdb_account.main.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
}

# Cosmos DB Container
resource "azurerm_cosmosdb_sql_container" "letters" {
  name                  = "letters"
  resource_group_name   = azurerm_cosmosdb_account.main.resource_group_name
  account_name          = azurerm_cosmosdb_account.main.name
  database_name         = azurerm_cosmosdb_sql_database.main.name
  partition_key_path    = "/type"
  partition_key_version = 1

  indexing_policy {
    indexing_mode = "consistent"

    included_path {
      path = "/*"
    }

    included_path {
      path = "/created_at/?"
    }

    included_path {
      path = "/letter_type/?"
    }
  }
}

# Static Web App for Frontend
resource "azurerm_static_site" "frontend" {
  name                = "${var.project_name}-${var.environment}-frontend"
  resource_group_name = azurerm_resource_group.main.name
  location            = "eastus2"  # Static Web Apps have limited region support
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = var.tags
}

# API Management (Consumption Tier)
resource "azurerm_api_management" "main" {
  count               = var.deploy_apim ? 1 : 0
  name                = "${var.project_name}-${var.environment}-apim"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = var.apim_publisher_name
  publisher_email     = var.apim_publisher_email
  sku_name            = "Consumption_0"
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

# API Management API
resource "azurerm_api_management_api" "function_api" {
  count               = var.deploy_apim ? 1 : 0
  name                = "insurance-letters-api"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main[0].name
  revision            = "1"
  display_name        = "Insurance Letters API"
  path                = "api"
  protocols           = ["https"]
  
  subscription_required = false
}

# API Management Backend
resource "azurerm_api_management_backend" "function_backend" {
  count               = var.deploy_apim ? 1 : 0
  name                = "function-app-backend"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main[0].name
  protocol            = "http"
  url                 = "https://${azurerm_linux_function_app.main.default_hostname}/api"
  
  credentials {
    header = {
      "x-functions-key" = azurerm_linux_function_app.main.host_keys["default"]
    }
  }
}

# API Management Operations
locals {
  api_operations = {
    "health" = {
      method = "GET"
      url_template = "/health"
    }
    "debug-token" = {
      method = "POST"
      url_template = "/debug-token"
    }
    "draft-letter" = {
      method = "POST"
      url_template = "/draft-letter"
    }
    "suggest-letter-type" = {
      method = "POST"
      url_template = "/suggest-letter-type"
    }
    "validate-letter" = {
      method = "POST"
      url_template = "/validate-letter"
    }
  }
}

resource "azurerm_api_management_api_operation" "operations" {
  for_each            = var.deploy_apim ? local.api_operations : {}
  operation_id        = each.key
  api_name            = azurerm_api_management_api.function_api[0].name
  api_management_name = azurerm_api_management.main[0].name
  resource_group_name = azurerm_resource_group.main.name
  display_name        = each.key
  method              = each.value.method
  url_template        = each.value.url_template
}

# API Management Policy
resource "azurerm_api_management_api_policy" "api_policy" {
  count               = var.deploy_apim ? 1 : 0
  api_name            = azurerm_api_management_api.function_api[0].name
  api_management_name = azurerm_api_management.main[0].name
  resource_group_name = azurerm_resource_group.main.name

  xml_content = templatefile("${path.module}/apim-policies.xml", {
    azure_ad_tenant_id = var.azure_ad_tenant_id
    azure_ad_client_id = var.azure_ad_client_id
    backend_id         = azurerm_api_management_backend.function_backend[0].name
    allowed_origins    = jsonencode(concat(
      ["https://${azurerm_static_site.frontend.default_host_name}"],
      var.additional_cors_origins
    ))
  })
}