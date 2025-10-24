# TTN Webhook Setup Guide

## Option A: Using ngrok (Easiest for Testing)

1. **Install ngrok on your Jetson:**
```bash
# Download and install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

2. **Start your webhook server:**
```bash
python3 jetson_webhook_server.py
```

3. **In another terminal, expose it with ngrok:**
```bash
ngrok http 8000
```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

## Option B: Using Cloudflare Tunnel (Free alternative)

1. **Install cloudflared:**
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

2. **Login to Cloudflare:**
```bash
cloudflared tunnel login
```

3. **Create and run tunnel:**
```bash
cloudflared tunnel --url http://localhost:8000
```

## Option C: Router Port Forwarding

1. **Set static IP** for your Jetson in router settings
2. **Forward port 8000** to your Jetson's IP
3. **Use your public IP** or get a dynamic DNS service

## TTN Webhook Configuration

Once you have a public URL (e.g., `https://abc123.ngrok.io`):

1. **Go to TTN Console** → Your Application → Integrations
2. **Click "Add integration"** → **Webhooks**
3. **Configure the webhook:**
   - **Webhook ID**: `jetson-receiver`
   - **Webhook base URL**: `https://abc123.ngrok.io/webhook`
   - **Downlink API key**: (your TTN API key)
   - **Enabled**: ✅

4. **Select message types:**
   - ✅ `as.up.data.forward` (uplink messages)
   - ✅ `join.accept` (optional)
   - ✅ `join.reject` (optional)

## Testing the Webhook

Test your endpoint:
```bash
curl -X POST https://abc123.ngrok.io/webhook/lorawan \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Advanced Security

Add authentication to your webhook endpoint:

```python
@app.post("/webhook/lorawan")
async def receive_lorawan_data(request: Request):
    # Verify TTN webhook signature
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Continue with processing...
```


