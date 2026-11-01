"""Objects and fields to extract from Salesforce."""

OBJECTS = {
    "Account": ["Id", "Name", "Industry", "AnnualRevenue", "BillingCountry",
                "IsDeleted", "SystemModstamp"],
    "Opportunity": ["Id", "AccountId", "Name", "StageName", "Amount", "CloseDate",
                    "IsClosed", "IsWon", "IsDeleted", "SystemModstamp"],
}
REQUIRED_FIELDS = ["Id", "SystemModstamp"]
DEFAULT_WATERMARK = "1970-01-01T00:00:00Z"
