# Push the HealthLens-LLM Docker image to Amazon ECR.
# Run from the repository root, or call with an absolute path to this script.
#
# Example:
#   powershell -ExecutionPolicy Bypass -File scripts/push_ecr.ps1

$ErrorActionPreference = "Stop"

# Avoid AWS CLI opening a pager during scripted runs.
$env:AWS_PAGER = ""

function Invoke-NativeCommand {
    <#
    Run a native executable without PowerShell treating stderr as a terminating error.
    Returns the process exit code.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Command
        return $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

# Default configuration (override by setting these variables before running the script).
$Region = if ($env:AWS_REGION) { $env:AWS_REGION } else { "eu-west-2" }
$RepositoryName = if ($env:ECR_REPOSITORY) { $env:ECR_REPOSITORY } else { "healthlens-llm" }
$LocalImageName = if ($env:DOCKER_IMAGE_NAME) { $env:DOCKER_IMAGE_NAME } else { "healthlens-llm" }
$ImageTag = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "latest" }

# Resolve repository root so Docker build always uses the project Dockerfile.
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "HealthLens-LLM ECR push helper"
Write-Host "Repository root: $RepoRoot"
Write-Host "AWS region: $Region"
Write-Host "ECR repository: $RepositoryName"
Write-Host "Local image: ${LocalImageName}:${ImageTag}"
Write-Host ""

# Step 1: Verify Docker CLI is installed.
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not on PATH. Install Docker Desktop for Windows first."
}

# Step 2: Verify AWS CLI is installed.
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    throw "AWS CLI is not installed or not on PATH. Install AWS CLI v2 first."
}

# Step 3: Verify Docker Engine is running.
Write-Host "Checking Docker Engine..."
docker info | Out-Null
Write-Host "Docker Engine is running."
Write-Host ""

# Step 4: Verify AWS credentials and read the current account ID.
Write-Host "Checking AWS identity..."
$IdentityJson = aws sts get-caller-identity --output json | ConvertFrom-Json
$AccountId = $IdentityJson.Account
$CallerArn = $IdentityJson.Arn
Write-Host "AWS account: $AccountId"
Write-Host "Caller: $CallerArn"
Write-Host ""

# Step 5: Build the ECR registry URI for this account and region.
$RegistryUri = "${AccountId}.dkr.ecr.${Region}.amazonaws.com"
$RemoteImageUri = "${RegistryUri}/${RepositoryName}:${ImageTag}"

# Step 6: Create the ECR repository if it does not already exist.
Write-Host "Ensuring ECR repository exists..."
$DescribeExitCode = Invoke-NativeCommand {
    aws ecr describe-repositories `
        --repository-names $RepositoryName `
        --region $Region `
        2>&1 | Out-Null
}

if ($DescribeExitCode -ne 0) {
    Write-Host "Repository not found. Creating $RepositoryName..."
    $CreateExitCode = Invoke-NativeCommand {
        aws ecr create-repository `
            --repository-name $RepositoryName `
            --region $Region `
            --image-scanning-configuration scanOnPush=true `
            2>&1 | Out-Null
    }
    if ($CreateExitCode -ne 0) {
        throw "Failed to create ECR repository '$RepositoryName' in region '$Region'."
    }
    Write-Host "ECR repository created."
} else {
    Write-Host "ECR repository already exists."
}
Write-Host ""

# Step 7: Authenticate Docker to Amazon ECR.
Write-Host "Logging Docker in to Amazon ECR..."
$LoginPassword = aws ecr get-login-password --region $Region
$LoginPassword | docker login --username AWS --password-stdin $RegistryUri | Out-Null
Write-Host "Docker login successful."
Write-Host ""

# Step 8: Build the Docker image from the repository Dockerfile.
Write-Host "Building Docker image..."
docker build -t "${LocalImageName}:${ImageTag}" .
Write-Host "Docker build complete."
Write-Host ""

# Step 9: Tag the local image for ECR.
Write-Host "Tagging image for ECR..."
docker tag "${LocalImageName}:${ImageTag}" $RemoteImageUri
Write-Host "Tagged as $RemoteImageUri"
Write-Host ""

# Step 10: Push the image to Amazon ECR.
Write-Host "Pushing image to ECR..."
docker push $RemoteImageUri
Write-Host ""

# Step 11: Print the final image URI for ECS deployment.
Write-Host "Push complete."
Write-Host "ECR image URI:"
Write-Host $RemoteImageUri
