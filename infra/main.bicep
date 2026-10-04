targetScope = 'resourceGroup'

param location string = resourceGroup().location
param accountName string
param projectName string
param runId string
param chatModel string
param chatVersion string
param judgeModel string
param judgeVersion string
param embeddingModel string
param embeddingVersion string
@allowed(['GlobalStandard', 'DataZoneStandard', 'Standard'])
param modelSku string
@minValue(1)
@maxValue(10000)
param chatCapacity int
@minValue(1)
@maxValue(10000)
param judgeCapacity int
@minValue(1)
@maxValue(10000)
param embeddingCapacity int

param preservedDeployments object = {
  chat: { properties: {}, sku: {}, tags: {} }
  judge: { properties: {}, sku: {}, tags: {} }
  embedding: { properties: {}, sku: {}, tags: {} }
}

var ownership = {
  repository: 'microsoft-foundry-labs-v1.5'
  scenario: 'Contoso'
  validationRun: runId
  retention: 'retain-until-explicit-approval'
}

resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: accountName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  tags: ownership
  properties: {
    customSubDomainName: accountName
    allowProjectManagement: true
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: account
  name: projectName
  location: location
  identity: { type: 'SystemAssigned' }
  tags: ownership
  properties: {
    displayName: 'Contoso independent workshop'
    description: 'Synthetic purchasing, policy, inventory and draft-only validation'
  }
}

resource chat 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: 'contoso-chat'
  sku: union(preservedDeployments.chat.sku, { name: modelSku, capacity: chatCapacity })
  tags: union(preservedDeployments.chat.tags, ownership)
  properties: union(preservedDeployments.chat.properties, {
    model: { format: 'OpenAI', name: chatModel, version: chatVersion }
    versionUpgradeOption: 'NoAutoUpgrade'
  })
  dependsOn: [project]
}

resource judge 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: 'contoso-judge'
  sku: union(preservedDeployments.judge.sku, { name: modelSku, capacity: judgeCapacity })
  tags: union(preservedDeployments.judge.tags, ownership)
  properties: union(preservedDeployments.judge.properties, {
    model: { format: 'OpenAI', name: judgeModel, version: judgeVersion }
    versionUpgradeOption: 'NoAutoUpgrade'
  })
  dependsOn: [chat]
}

resource embedding 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: 'contoso-embedding'
  sku: union(preservedDeployments.embedding.sku, { name: modelSku, capacity: embeddingCapacity })
  tags: union(preservedDeployments.embedding.tags, ownership)
  properties: union(preservedDeployments.embedding.properties, {
    model: { format: 'OpenAI', name: embeddingModel, version: embeddingVersion }
    versionUpgradeOption: 'NoAutoUpgrade'
  })
  dependsOn: [judge]
}

output accountId string = account.id
output projectId string = project.id
output projectPrincipalId string = project.identity.principalId
output accountEndpoint string = account.properties.endpoint
