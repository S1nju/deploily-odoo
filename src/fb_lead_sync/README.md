# Facebook Lead Sync — Odoo Module

## What This Module Does

This custom Odoo module connects your **Facebook Lead Ads** forms directly to **Odoo CRM**.

Every day at midnight, it automatically:
1. Calls the Facebook Graph API
2. Fetches all new leads submitted in the last 24 hours from your Lead Ad form
3. Creates them as **CRM Leads** in Odoo
4. Logs each sync with details (how many found, created, skipped)

---

## Installation

1. Copy the `fb_lead_sync` folder into your Odoo `addons` directory
2. Restart the Odoo server
3. Go to **Apps** → search for "Facebook Lead Sync" → click **Install**

---

## Configuration (Settings)

Go to **Settings** → scroll down to **Facebook Lead Ads Integration**

Fill in the following fields:

| Field | Where to find it |
|-------|-----------------|
| **Facebook App ID** | developers.facebook.com → Your App → Settings → Basic |
| **Facebook App Secret** | Same page as above |
| **Page Access Token** | Meta Business Suite → Settings → Page Access Token (must be a long-lived token) |
| **Ad Account ID** | Meta Ads Manager → top left dropdown (format: `act_XXXXXXXXX`) |
| **Lead Form ID** | Meta Ads Manager → Lead Centre → Lead Ad Forms → click your form → copy ID from URL |
| **Default Sales Team** | Select from your existing Odoo sales teams |
| **Default Salesperson** | Select from your Odoo users |

Then toggle **Enable Daily Sync** to ON and click **Save**.

---

## How to Get a Long-Lived Access Token

1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your App and your Page
3. Generate a short-lived token with permissions: `ads_management`, `leads_retrieval`, `pages_read_engagement`
4. Use the [Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) to exchange it for a long-lived token (60 days)
5. Paste the long-lived token into Odoo Settings

> ⚠️ You need to **refresh the token every ~60 days** or set up a system to auto-refresh it.

---

## Viewing Sync Logs

Go to **CRM → Facebook Sync Logs** to see:
- Date and time of each sync
- How many leads were found / created / skipped (already existed)
- Any errors with their details

---

## How Duplicate Prevention Works

When a lead is created, the module stores the Facebook Lead ID in the lead's **description** field (e.g., `fb_lead_id:1234567890`). Before creating a new lead, it checks if that ID already exists — so the same person is never imported twice.

---

## Field Mapping

The module automatically maps these Facebook form field names to Odoo:

| Facebook Field Name | Odoo Field |
|--------------------|------------|
| `email` / `email_address` | Email |
| `phone_number` / `phone` / `mobile` | Phone |
| `first_name` + `last_name` / `full_name` | Contact Name |
| `city` | City |

All other form fields are stored in the lead **Description** for reference.

---

## Requirements

- Odoo 16.0
- Python `requests` library (included in standard Odoo)
- A Facebook Developer App with `leads_retrieval` permission approved
