$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$downloads = "$env:USERPROFILE\Downloads"

# Cria a pasta de destino se não existir
New-Item -ItemType Directory -Force -Path $downloads | Out-Null

# Ruff check (lint)
python -m ruff check app/ 2>&1 | Out-File -FilePath "$downloads\ruff_errors_$timestamp.txt" -Encoding utf8
Write-Host "Lint errors saved to: $downloads\ruff_errors_$timestamp.txt"

# Ruff format check
python -m ruff format app/ --check 2>&1 | Out-File -FilePath "$downloads\ruff_format_$timestamp.txt" -Encoding utf8
Write-Host "Format errors saved to: $downloads\ruff_format_$timestamp.txt"

# Run pre-commit and save output
python -m pre_commit run --all-files 2>&1 | Out-File -FilePath "$downloads\precommit_$timestamp.txt" -Encoding utf8
Write-Host "Pre-commit output saved to: $downloads\precommit_$timestamp.txt"
