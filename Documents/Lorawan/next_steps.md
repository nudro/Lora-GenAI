# Next Steps: Configure DRAGINO for SE01-LB Soil Sensor

## Current Issue: Internet and IoT service showing "X"

### Step 1: Fix Internet Connection
**In DRAGINO Interface:**
1. Go to: **System → WiFi → WiFi WAN Client Settings**
2. Click **"WiFi Survey"** to scan for your home network
3. Select your home WiFi network from the list
4. Enter your WiFi password
5. Click **"Save & Apply"**
6. Wait 2-3 minutes for connection

**OR** Connect Ethernet cable from DRAGINO to your router

### Step 2: Get Gateway Information
**In DRAGINO Interface:**
1. Go to: **LoRaWAN → LoRaWAN** (or just "LoRaWAN" menu)
2. **Note the Gateway EUI** - looks like: `a840411e96744154`
3. This is needed to register gateway with TTN

### Step 3: Register Gateway on The Things Network (TTN)
**No software download needed - TTN is web-based:**

1. **Go to**: https://console.thethingsnetwork.org
2. **Create account** if you don't have one
3. **Choose cluster** (Region):
   - US: `nam1.cloud.thethings.network`
   - Europe: `eu1.cloud.thethings.network`
   - Asia: `au1.cloud.thethings.network`

4. **Add Gateway**:
   - Click "Gateways" → "Add gateway"
   - Enter Gateway EUI from DRAGINO
   - Choose frequency plan (likely US915 for North America)
   - Save

5. **Get server keys** from TTN gateway page (CUPS/LNS keys)

### Step 4: Configure DRAGINO LoRaWAN Settings
**Back in DRAGINO Interface:**
1. Go to: **LoRaWAN → LoRaWAN** settings
2. **Enter TTN server info**:
   - Server address: `nam1.cloud.thethings.network` (or appropriate region)
   - CUPS URI and Key (from TTN gateway page)
   - LNS URI and Key (from TTN gateway page)
3. **Save & Apply**

### Step 5: Register SE01-LB Sensor
**Get sensor info from device/sticker:**
- DEV EUI
- APP EUI  
- APP KEY

**In TTN Console:**
1. Create Application (if needed)
2. Add End Device with sensor information
3. Choose appropriate frequency plan

### Expected Results:
- Internet connection: ✅ Green checkmark
- IoT service: ✅ Green checkmark  
- SYS LED: 🔵 Solid blue (connected to LoRaWAN server)
- LORA LED: 🟢 Flashes when receiving sensor data

## SE01-LB Specific Notes:
This is likely a Dragino SE01-LB soil sensor that uses standard LoRaWAN OTAA join procedure.


