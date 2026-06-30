# Rule — Data Quality

A record is only marked Verified when it has:
- contact.name confirmed
- company.name confirmed
- contact.email OR contact.linkedin (one minimum)
- company.channel_presence confirmed
- company.categories confirmed
- gtm.icp_score set (not null)

A record with any of the above missing is Needs Review.
A record missing contact.name OR company.name is Incomplete
and does not enter any workflow.

The agent never guesses, infers, or fills missing fields.
Null means null. Surface it and move on.
