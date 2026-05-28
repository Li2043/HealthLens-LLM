# Build, test, push HealthLens-LLM to Amazon ECR, and force a new ECS deployment.
# Run from the repository root, or call with an absolute path to this script.
#
# Example:
#   powershell -ExecutionPolicy Bypass -File scripts/deploy_ecr_ecs.ps1
#
# Override defaults before running:
#   $env:AWS_REGION = "eu-west-2"
#   $env:ECR_REPOSITORY = "healthlens-llm"
#   $env:ECS_SERVICE_NAME = "healthlens-llm"

$ErrorActionPreference = "Stop"

# --- Configurable settings (override via environment variables) ---
$EcsServiceName = if ($env:ECS_SERVICE_NAME) { $env:ECS_SERVICE_NAME } else { "healthlens-llm" }
$EcsClusterName = if ($env:ECS_CLUSTER_NAME) { $env:ECS_CLUSTER_NAME } else { "default" }

$Region = if ($env:AWS_REGION) { $env:AWS_REGION } else { "eu-west-2" }
$RepositoryName = if ($env:ECR_REPOSITORY) { $env:ECR_REPOSITORY } else { "healthlens-llm" }
$LocalImageName = if ($env:DOCKER_IMAGE_NAME) { $env:DOCKER_IMAGE_NAME } else { "healthlens-llm" }
$ImageTag = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "latest" }

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

function Invoke-Pytest {
    $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        & $venvPython -m pytest -v
    } else {
        python -m pytest -v
    }

    if ($LASTEXITCODE -ne 0) {
        throw "pytest failed with exit code $LASTEXITCODE. Deployment aborted."
    }
}

# Resolve repository root so commands always run from the project root.
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "HealthLens-LLM deploy helper (ECR + ECS)"
Write-Host "Repository root: $RepoRoot"
Write-Host "AWS region: $Region"
Write-Host "ECR repository: $RepositoryName"
Write-Host "Local image: ${LocalImageName}:${ImageTag}"
Write-Host "ECS cluster: $EcsClusterName"
Write-Host "ECS service: $EcsServiceName"
Write-Host ""

# Step 1: Verify required tools are installed.
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not on PATH. Install Docker Desktop for Windows first."
}

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    throw "AWS CLI is not installed or not on PATH. Install AWS CLI v2 first."
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or not on PATH. Install Python 3.12+ first."
}

Write-Host "Checking Docker Engine..."
docker info | Out-Null
Write-Host "Docker Engine is running."
Write-Host ""

# Step 2: Run tests before building or deploying.
Write-Host "Running tests..."
Invoke-Pytest
Write-Host "All tests passed."
Write-Host ""

# Step 3: Build the Docker image.
Write-Host "Building Docker image..."
docker build -t "${LocalImageName}:${ImageTag}" .
Write-Host "Docker build complete."
Write-Host ""

# Step 4: Verify AWS credentials and read the current account ID.
Write-Host "Checking AWS identity..."
$IdentityJson = aws sts get-caller-identity --output json | ConvertFrom-Json
$AccountId = $IdentityJson.Account
$CallerArn = $IdentityJson.Arn
Write-Host "AWS account: $AccountId"
Write-Host "Caller: $CallerArn"
Write-Host ""

$RegistryUri = "${AccountId}.dkr.ecr.${Region}.amazonaws.com"
$RemoteImageUri = "${RegistryUri}/${RepositoryName}:${ImageTag}"

# Step 5: Ensure the ECR repository exists.
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

# Step 6: Log Docker in to Amazon ECR.
Write-Host "Logging Docker in to Amazon ECR..."
$LoginPassword = aws ecr get-login-password --region $Region
$LoginPassword | docker login --username AWS --password-stdin $RegistryUri | Out-Null
Write-Host "Docker login successful."
Write-Host ""

# Step 7: Tag the local image for ECR.
Write-Host "Tagging image for ECR..."
docker tag "${LocalImageName}:${ImageTag}" $RemoteImageUri
Write-Host "Tagged as $RemoteImageUri"
Write-Host ""

# Step 8: Push the image to Amazon ECR.
Write-Host "Pushing image to ECR..."
docker push $RemoteImageUri
Write-Host "Push complete."
Write-Host ""

# Step 9: Force a new ECS deployment.
Write-Host "Forcing new ECS deployment..."
$UpdateExitCode = Invoke-NativeCommand {
    aws ecs update-service `
        --cluster $EcsClusterName `
        --service $EcsServiceName `
        --force-new-deployment `
        --region $Region `
        2>&1 | Out-Null
}

if ($UpdateExitCode -ne 0) {
    throw "Failed to update ECS service '$EcsServiceName' in cluster '$EcsClusterName' (region '$Region')."
}

Write-Host "ECS deployment triggered successfully."
Write-Host ""

# Step 10: Print final details and verification reminders.
Write-Host "Deployment complete."
Write-Host "ECR image URI:"
Write-Host $RemoteImageUri
Write-Host ""
Write-Host "After the new task starts, verify your public URL:"
Write-Host "  - GET /health   (container health check)"
Write-Host "  - GET /version  (safe runtime metadata)"
Write-Host "  - GET /         (homepage / frontend)"
Write-Host ""
Write-Host "Example checks (replace with your ECS public URL):"
Write-Host "  curl https://<your-ecs-url>/health"
Write-Host "  curl https://<your-ecs-url>/version"
