targetScope = 'resourceGroup'

param location string = resourceGroup().location
param accountName string
param projectName string
param runId string

var ownership = {
  repository: 'foundry-labs-v1.5'
  scenario: 'Contoso'
  validationRun: runId
  retention: 'retain-until-explicit-approval'
}

resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: accountName
}
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' existing = {
  parent: account
  name: projectName
}
resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${runId}'
  location: location
  tags: ownership
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    workspaceCapping: { dailyQuotaGb: 1 }
  }
}
resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${runId}'
  location: location
  kind: 'web'
  tags: ownership
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
    IngestionMode: 'LogAnalytics'
  }
}
resource connection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: project
  name: 'contoso-tracing'
  properties: {
    category: 'AppInsights'
    target: insights.id
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: { key: insights.properties.ConnectionString }
    metadata: { ApiType: 'Azure', ResourceId: insights.id }
  }
}
output appInsightsId string = insights.id
output appId string = insights.properties.AppId
output workspaceId string = workspace.id
