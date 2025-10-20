# DRAGINO LoRaWAN Gateway Setup Guide

## Overview
This guide covers setting up a DRAGINO LPS8 LoRaWAN Gateway to connect with LoRaWAN soil sensors. The recommended approach is **WiFi connection only** for simplicity and reliability.

## Prerequisites
- DRAGINO LPS8 Gateway
- USB WiFi adapter (if your computer doesn't have built-in WiFi)
- LoRaWAN soil sensors with known EUI and keys

## Step 1: Connect to DRAGINO Gateway via WiFi

### 1.1 Physical Setup
1. **Power on the DRAGINO gateway**
2. **Connect your USB WiFi adapter** if needed
3. **Ensure the DRAGINO has internet access** (via Ethernet to router or WiFi to router)

### 1.2 Find and Connect to DRAGINO WiFi
1. **Scan for WiFi networks** - look for network named `dragino-xxxxxx` (e.g., `dragino-2a7510`)
2. **Connect to the network** using password: `dragino+dragino`
3. **Wait for connection** - your device should get an IP like `10.130.1.xxx`

### 1.3 Fix Routing Issues (if needed)
If you cannot access the gateway interface, remove conflicting routes:
```bash
sudo ip route del 10.130.1.0/24 via [your-router-ip] dev [ethernet-interface]
```

## Step 2: Access Gateway Configuration

### 2.1 Open Gateway Interface
1. **Open your web browser**
2. **Navigate to**: `http://10.130.1.1`
3. **Login with**:
   - Username: `root`
   - Password: `dragino`

## Step 3: Configure LoRaWAN Network Server

### 3.1 Choose Network Server
- **Recommended**: The Things Network (TTN) v3 - free and widely used
- **Alternative**: ChirpStack, AWS IoT Core for LoRaWAN

### 3.2 The Things Network Setup
1. **Create account**: Go to [console.thethingsnetwork.org](https://console.thethingsnetwork.org)
2. **Choose cluster**: 
   - Europe: `eu1.cloud.thethings.network`
   - North America: `nam1.cloud.thethings.network`
   - Asia Pacific: `au1.cloud.thethings.network`

### 3.3 Register Gateway
1. **Get Gateway EUI**:
   - In DRAGINO interface, go to **LoRaWAN settings**
   - Note the Gateway EUI (e.g., `a840411e96744154`)

2. **Register on TTN**:
   - Click **Add Gateway** in TTN console
   - Enter Gateway EUI and choose appropriate frequency plan
   - Note down the **CUPS URI**, **CUPS Key**, **LNS URI**, and **LNS Key**

### 3.4 Configure Gateway Connection
1. **In DRAGINO interface**, go to **LoRaWAN → LoRaWAN** settings
2. **Use the correct configuration method**:
   - **Mode**: "LoRaWAN Semtech UDP" (from dropdown)
   - **Primary LoRaWAN Server**: "Custom / Private LoRaWAN"
   - **Server Address**: `nam1.cloud.thethings.network` (US region, no https:// prefix)
   - **For EU region**: `eu1.cloud.thethings.network`
   - **For Asia**: `au1.cloud.thethings.network`
3. **Enter TTN credentials** (if required):
   - API keys from TTN gateway registration
4. **Save and apply** settings
5. **Wait 2-3 minutes** for connection

## Step 4: Verify Gateway Connection

### 4.1 Check LED Status
- **POWER LED (RED)**: Solid on ✅
- **SYS LED**: Should be **SOLID BLUE** when connected to LoRaWAN server ✅
- **LORA LED**: Will flash green when receiving packets (once sensors are connected)
- **ETH LED**: Shows network activity

### 4.2 Verify in TTN Console
- Check TTN console to confirm gateway shows as "Connected"

## Step 5: Register Soil Sensors

### 5.1 Obtain Sensor Information
Find these identifiers on your soil sensor (usually on sticker or documentation):
- **DEV EUI**: Device Extended Unique Identifier
- **APP EUI**: Application Extended Unique Identifier  
- **APP KEY**: Application Key

### 5.2 Register Device in TTN
1. **In TTN console**, go to your Application
2. **Click "Add end device"**
3. **Enter device information**:
   - DEV EUI
   - APP EUI
   - APP KEY
4. **Choose appropriate frequency plan** and regional parameters
5. **Save registration**

## Step 6: Connect and Test Sensors

### 6.1 Power On Sensor
1. **Power on soil sensor** (use jumper JP2 or power switch if available)
2. **Wait for join request** - sensor should automatically attempt to join network

### 6.2 Monitor Connection
1. **Check TTN console** for incoming join requests and data
2. **In TTN console**, look for these tabs:
   - **"Live data"** - shows sensor readings
   - **"Events"** - shows join requests and network activity
3. **Verify in DRAGINO interface** - LORA LED should flash when receiving packets
4. **Check sensor data** appears in TTN console
5. **Be patient** - soil sensors typically transmit every 10-30 minutes to save battery

## LED Status Reference

### DRAGINO LPS8 LED Indicators:
- **POWER LED (RED)**: Solid = device powered on
- **SYS LED**: 
  - **Solid BLUE**: Connected to LoRaWAN server ✅ (Goal)
  - **Blinking BLUE**: Has internet but no LoRaWAN connection
  - **Solid RED**: No internet connection
- **LORA LED**: 
  - **Flashes GREEN**: Receiving/sending LoRa packets ✅ (Normal)
  - **Solid RED**: LoRaWAN module error (usually AppEUI mismatch) ❌
- **ETH LED**: Shows Ethernet/WiFi network activity

## Troubleshooting

### Cannot Access Gateway Interface
1. **Check WiFi connection** is stable
2. **Clear browser cache** and try again
3. **Try different browser** or incognito mode
4. **Remove routing conflicts** (see Step 1.3)

### Gateway Cannot Connect to TTN
1. **Verify internet connection** - SYS LED should not be solid red
2. **Check server address** matches chosen TTN cluster
3. **Verify CUPS/LNS keys** are entered correctly
4. **Wait 5-10 minutes** for connection to establish

### Sensors Not Joining
1. **Verify sensor EUI/keys** are entered correctly in TTN
2. **Check frequency plan** matches sensor requirements
3. **Ensure sensor is powered** and within range (1-2km typically)
4. **Verify gateway is connected** to TTN (SYS LED solid blue)

### LoRa LED is Red (Critical Issue)
If the **LoRa LED is solid RED**, this indicates a problem with the LoRaWAN module:

1. **Check DRAGINO logs** for join request details:
   - Go to DRAGINO interface → **System → Log**
   - Look for `[MACINFO~][JOIN_REQ]` entries
   - Note the **AppEUI** in the logs (e.g., `A840410000000101`)

2. **Fix AppEUI mismatch** (common issue):
   - Compare the AppEUI in DRAGINO logs with what you entered in TTN
   - **Update TTN device registration** to use the correct AppEUI from logs
   - **Do NOT use** `0000000000000000` if the sensor sends a different AppEUI

3. **Fix MIC mismatch** (APP KEY error):
   - If TTN shows `"name": "mic_mismatch"` error, the **APP KEY** is wrong
   - **Check the sensor label/sticker** for the correct APP KEY
   - **OR** if the sensor came with no APP KEY, you may need to program it:
     - Some sensors come with default keys that need to be updated
     - Check manufacturer documentation for default APP KEY

4. **Verify all identifiers match**:
   - **DEV EUI**: Must match exactly (case-insensitive)
   - **APP EUI** (Join EUI): Must match exactly from logs
   - **APP KEY**: Must match the sensor's programmed key exactly

5. **Restart sensor** after fixing registration:
   - Press the sensor's button or power cycle
   - Wait for new join requests

**Expected Result**: LoRa LED should blink GREEN when receiving packets

### LoRa LED Still Red After Successful Connection
If the LoRa LED remains red despite successful TTN activity:
1. **Check if device actually joined**: Look for `"ns.up.join.accept"` events in TTN
2. **The LED behavior may vary**: Some DRAGINO firmware versions show red LED differently
3. **Focus on TTN console activity**: If you see `"ns.down.transmission.success"` events, the connection is working
4. **Wait for regular sensor data**: The LED typically turns green when receiving uplink data packets, not just join/network traffic

### TTN Event Messages Explained
- **`"mic_mismatch"`**: APP KEY doesn't match between sensor and TTN registration ❌
- **`"join_cluster_fail"`**: Usually caused by mic_mismatch (wrong APP KEY) ❌
- **`"ns.down.transmission.success"`**: **SUCCESS** - TTN successfully sent downlink to device ✅
- **`"ns.up.join.accept"`**: **SUCCESS** - Device successfully joined the network ✅
- **`"not_found"`**: Device EUI not registered in TTN ❌

### SE01-LB Sensor Specific Notes
- **DEV EUI**: Usually on the sensor label (e.g., `A8404187D55BBA3B`)
- **SN**: Serial number on label (e.g., `LA6660...`)
- **APP EUI**: Check DRAGINO logs for what the sensor actually sends
- **APP KEY**: May need to be programmed into the sensor or found in documentation

#### Expected Data Transmission Intervals
- **Soil sensors typically send data every 10-30 minutes** to conserve battery
- **9 minutes between transmissions is normal** for battery-powered sensors
- **Don't worry if you see gaps** - this is expected behavior
- **Sensor may sleep between measurements** to extend battery life

## Next Steps
Once everything is working:
- Monitor sensor data in TTN console
- Set up data visualization or forwarding
- Configure alerts if needed
- Document sensor locations and readings

## Files in This Directory
- `README.md` - This guide
- `LPS8_LoRaWAN_Gateway_User_Manual_v1.3.2.pdf` - Official DRAGINO manual
- `LPS8_LoRaWAN_Gateway_User_Manual_v1.3.2.txt` - Extracted text from manual
- `pdf_to_text.py` - Script used to extract PDF text
