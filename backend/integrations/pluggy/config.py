base_url = "https://api.pluggy.ai"

# Webhooks our backend registers at Pluggy (single source for the registration and the routes)
webhook_token_header = "X-Webhook-Token"
item_created_webhook_path = "/webhooks/pluggy/items/created"
item_updated_webhook_path = "/webhooks/pluggy/items/updated"
item_deleted_webhook_path = "/webhooks/pluggy/items/deleted"

# Pluggy event -> route of this backend that receives it
item_webhook_paths = {
    "item/created": item_created_webhook_path,
    "item/updated": item_updated_webhook_path,
    "item/deleted": item_deleted_webhook_path,
}
