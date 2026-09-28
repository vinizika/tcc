"""Explicit administrative verification; never run automatically from signup."""
import argparse
from datetime import datetime, timezone

from app.core.config import settings
from app.clients.mongo_client import get_mongo_database
from app.clients.supabase_client import get_supabase_client
from app.repositories.workflow_repository import get_workflow_repository


def main():
    parser = argparse.ArgumentParser(description="Record a completed manual clinic verification.")
    parser.add_argument("--clinic-id", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--evidence-reference", required=True, help="Reference to a restricted verification record, not a personal document.")
    parser.add_argument("--confirm-ownership-checked", action="store_true", required=True)
    args = parser.parse_args()
    repo = get_workflow_repository()
    clinic = repo.get_clinic(args.clinic_id)
    if not clinic or clinic.get("source") == "demo":
        parser.error("Target must be an existing non-academic unit.")
    owner = clinic.get("owner_user_id")
    if not owner:
        parser.error("Unit does not have an institutional owner.")
    if settings.AUTH_PROVIDER == "local":
        accounts = get_mongo_database().poc_accounts
        account = accounts.find_one({"_id": owner, "role": "clinic", "clinic_id": clinic["id"]})
        if not account:
            parser.error("Account link is missing or belongs to a different unit.")
    else:
        profile = get_supabase_client().table("profiles").select("*").eq("user_id", owner).single().execute().data
        if not profile or profile.get("role") != "clinic" or profile.get("clinic_id") != clinic["id"]:
            parser.error("Institutional profile link is invalid.")
    clinic.update(verified=True, enabled=True, verification_status="verified", verification={
        "reviewer": args.reviewer, "evidence_reference": args.evidence_reference,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    })
    repo.save_clinic(clinic)
    if settings.AUTH_PROVIDER == "local":
        accounts.update_one({"_id": owner, "clinic_id": clinic["id"]}, {"$set": {"clinic_verified": True}})
    else:
        get_supabase_client().table("profiles").update({"clinic_verified": True}).eq("user_id", owner).execute()
    print("Verification recorded for unit:", clinic["id"])


if __name__ == "__main__":
    main()
