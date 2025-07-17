output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "function_app_name" {
  description = "The name of the Function App"
  value       = azurerm_linux_function_app.main.name
}

output "function_app_default_hostname" {
  description = "The default hostname of the Function App"
  value       = azurerm_linux_function_app.main.default_hostname
}

output "function_app_principal_id" {
  description = "The principal ID of the Function App's managed identity"
  value       = azurerm_linux_function_app.main.identity[0].principal_id
}

output "cosmos_db_endpoint" {
  description = "The endpoint of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.main.endpoint
}

output "cosmos_db_primary_key" {
  description = "The primary key of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.main.primary_key
  sensitive   = true
}

output "static_web_app_url" {
  description = "The URL of the static web app"
  value       = "https://${azurerm_static_site.frontend.default_host_name}"
}

output "static_web_app_api_key" {
  description = "The API key for deploying to the static web app"
  value       = azurerm_static_site.frontend.api_key
  sensitive   = true
}

output "application_insights_instrumentation_key" {
  description = "The instrumentation key for Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "The connection string for Application Insights"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "api_management_gateway_url" {
  description = "The gateway URL of the API Management instance"
  value       = var.deploy_apim ? azurerm_api_management.main[0].gateway_url : null
}

output "api_management_developer_portal_url" {
  description = "The developer portal URL of the API Management instance"
  value       = var.deploy_apim ? azurerm_api_management.main[0].developer_portal_url : null
}

output "deployment_instructions" {
  description = "Post-deployment instructions"
  value = <<-EOT
    
    Deployment completed! Next steps:
    
    1. Deploy Function App code:
       cd ../api
       func azure functionapp publish ${azurerm_linux_function_app.main.name}
    
    2. Build and deploy frontend:
       cd ../ui
       npm run build
       
       Then use the following deployment token to deploy:
       az staticwebapp deployment token show --name ${azurerm_static_site.frontend.name} --resource-group ${azurerm_resource_group.main.name}
    
    3. Configure Azure AD App Registration:
       - Add redirect URI: ${azurerm_static_site.frontend.default_host_name}/redirect
       - Add API permissions for your Function App
       - Update frontend environment variables
    
    4. Access your application:
       - Frontend: https://${azurerm_static_site.frontend.default_host_name}
       - API: ${var.deploy_apim ? azurerm_api_management.main[0].gateway_url : "https://${azurerm_linux_function_app.main.default_hostname}/api"}
       - Developer Portal: ${var.deploy_apim ? azurerm_api_management.main[0].developer_portal_url : "N/A"}
  EOT
}