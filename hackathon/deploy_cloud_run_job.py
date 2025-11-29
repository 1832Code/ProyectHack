"""
Script to deploy Instagram search to Google Cloud Run Jobs
Author: Mauricio J. @synaw_w
"""

import os
import subprocess
import sys
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from dotenv import load_dotenv

stderr_buffer = StringIO()
try:
    with redirect_stderr(stderr_buffer):
        load_dotenv(verbose=False)
except Exception:
    pass

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "us-central1")
JOB_NAME = os.getenv("CLOUD_RUN_JOB_NAME", "instagram-search")
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}", file=sys.stderr)
    return result


def check_prerequisites():
    if not PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not found in environment variables")
    if not APIFY_TOKEN:
        raise ValueError("APIFY_API_TOKEN not found in environment variables")
    
    try:
        run_command(["gcloud", "--version"], check=False)
    except FileNotFoundError:
        raise ValueError("gcloud CLI not found. Please install Google Cloud SDK")


def enable_required_apis():
    print("Enabling required Google Cloud APIs...")
    apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "artifactregistry.googleapis.com"
    ]
    
    for api in apis:
        try:
            run_command([
                "gcloud", "services", "enable", api,
                "--project", PROJECT_ID
            ], check=False)
        except Exception:
            pass


def create_or_update_job():
    print(f"\nCreating/updating Cloud Run Job: {JOB_NAME}")
    print("Building image automatically using Cloud Build (no Docker required locally)")
    
    enable_required_apis()
    
    cmd = [
        "gcloud", "run", "jobs", "deploy", JOB_NAME,
        "--source", ".",
        "--region", REGION,
        "--set-env-vars", f"APIFY_API_TOKEN={APIFY_TOKEN}",
        "--max-retries", "1",
        "--task-timeout", "3600",
        "--cpu", "2",
        "--memory", "4Gi"
    ]
    
    if PROJECT_ID:
        cmd.extend(["--project", PROJECT_ID])
    
    result = run_command(cmd, check=False)
    
    if result.returncode != 0:
        print("\n⚠️  Common issues to check:", file=sys.stderr)
        print("1. Make sure Cloud Run API is enabled: gcloud services enable run.googleapis.com", file=sys.stderr)
        print("2. Make sure Cloud Build API is enabled: gcloud services enable cloudbuild.googleapis.com", file=sys.stderr)
        print("3. Check your authentication: gcloud auth login", file=sys.stderr)
        print("4. Verify project permissions", file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    
    return result


def main():
    print("Starting Cloud Run Job deployment...")
    
    try:
        check_prerequisites()
        
        create_or_update_job()
        
        print(f"\n✅ Deployment successful!")
        print(f"Job name: {JOB_NAME}")
        print(f"Region: {REGION}")
        print(f"\nTo execute the job, run:")
        print(f"gcloud run jobs execute {JOB_NAME} --region {REGION} --project {PROJECT_ID}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment failed with exit code {e.returncode}", file=sys.stderr)
        if e.stdout:
            print(f"STDOUT: {e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"STDERR: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

