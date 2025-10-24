# Complete Guide: Setting Up a DRAGINO LoRaWAN Gateway with Soil Sensors

Setting up LoRaWAN infrastructure can seem daunting, but with the right guidance, you can have your DRAGINO LPS8 gateway connecting soil sensors to The Things Network in no time. This comprehensive guide will walk you through the entire process, from initial WiFi connection to troubleshooting common issues.

## What You'll Need

Before we begin, make sure you have:
- DRAGINO LPS8 Gateway
- USB WiFi adapter (if your computer doesn't have built-in WiFi)
- LoRaWAN soil sensors with known EUI and keys

## Part 1: Connecting to Your Gateway

### Initial WiFi Setup

The DRAGINO gateways create their own WiFi network out of the box. Here's how to connect:

1. **Power on your DRAGINO gateway** and scan for WiFi networks
2. **Look for a network** named `dragino-xxxxxx` (for example, `dragino-2a7510`)
3. **Connect using the password**: `dragino+dragino` (note the + symbol - this is crucial!)
4. **Wait for connection** - your device should automatically get an IP like `10.130.1.xxx`

### Accessing the Gateway Interface

Once connected to the DRAGINO's WiFi:

1. **Open your web browser** and navigate to `http://10.130.1.1`
2. **Login with**:
   - Username: `root`
   - Password: `dragino`

If you can't reach the interface, you might have routing conflicts. Remove conflicting routes with:
```bash
sudo ip route del 10.130.1.0/24 via [your-router-ip] dev [ethernet-interface]
```

## Part 2: Configuring The Things Network

### Setting Up TTN

The Things Network (TTN) is our recommended LoRaWAN network server - it's free and widely used:

1. **Create an account** at [console.thethingsnetwork.org](https://console.thethingsnetwork.org)
2. **Choose your cluster** based on location:
   - Europe: `eu1.cloud.thethings.network`
   - North America: `nam1.cloud.thethings.network`
   - Asia Pacific: `au1.cloud.thethings.network`

### Gateway Registration

Now let's register your gateway with TTN:

1. **Get your Gateway EUI**:
   - In the DRAGINO interface, go to **LoRaWAN settings**
   - Note the Gateway EUI (looks like `a840411e96744154`)

2. **Register on TTN**:
   - In TTN console, click **Add Gateway**
   - Enter your Gateway EUI and choose the appropriate frequency plan
   - Save the **CUPS URI**, **CUPS Key**, **LNS URI**, and **LNS Key** that TTN provides

### Gateway Connection Configuration

Back in your DRAGINO interface:

1. **Navigate to LoRaWAN → LoRaWAN** settings
2. **Configure the connection**:
   - **Mode**: "LoRaWAN Semtech UDP" (from the dropdown)
   - **Primary LoRaWAN Server**: "Custom / Private LoRaWAN"
   - **Server Address**: `nam1.cloud.thethings.network` (for US region, no https:// prefix)
3. **Enter your TTN credentials** if required
4. **Save and apply** settings
5. **Wait 2-3 minutes** for the connection to establish

## Part 3: LED Status Monitoring

Understanding your gateway's LED indicators is crucial for troubleshooting:

### LED Status Guide

- **POWER LED (RED)**: Solid = device powered on ✅
- **SYS LED**:
  - **Solid BLUE**: Connected to LoRaWAN server ✅ (This is your goal!)
  - **Blinking BLUE**: Has internet but no LoRaWAN connection
  - **Solid RED**: No internet connection
- **LORA LED**:
  - **Flashes GREEN**: Receiving/sending LoRa packets ✅ (Normal operation)
  - **Solid RED**: LoRaWAN module error (usually AppEUI mismatch) ❌
- **ETH LED**: Shows Ethernet/WiFi network activity

## Part 4: Adding Your Soil Sensors

### Gather Sensor Information

Before registering sensors, you'll need to find these identifiers on your soil sensor (usually on a sticker):

- **DEV EUI**: Device Extended Unique Identifier
- **APP EUI**: Application Extended Unique Identifier
- **APP KEY**: Application Key

### Device Registration in TTN

1. **In TTN console**, go to your Application
2. **Click "Add end device"**
3. **Enter device information**:
   - DEV EUI
   - APP EUI (we'll cover troubleshooting this later)
   - APP KEY
4. **Choose appropriate frequency plan** and regional parameters
5. **Save registration**

### Testing Your Sensors

1. **Power on your soil sensor** (use jumper JP2 or power switch if available)
2. **Monitor the TTN console** for incoming join requests and data
3. **Check the "Live data" tab** for sensor readings
4. **Be patient** - soil sensors typically transmit every 10-30 minutes to conserve battery

## Part 5: Troubleshooting Common Issues

### Issue: LoRa LED is Red

This is the most common problem and usually indicates an AppEUI mismatch:

1. **Check DRAGINO logs**:
   - Go to DRAGINO interface → **System → Log**
   - Look for `[MACINFO~][JOIN_REQ]` entries
   - Note the **AppEUI** in the logs (e.g., `A840410000000101`)

2. **Fix the AppEUI mismatch**:
   - Compare the AppEUI from DRAGINO logs with what you entered in TTN
   - **Update TTN device registration** to use the correct AppEUI from logs
   - **Don't use** `0000000000000000` if the sensor sends a different AppEUI

### Issue: MIC Mismatch Error

If you see `"mic_mismatch"` errors in TTN:

1. **The APP KEY is incorrect** - verify it matches what's programmed in the sensor
2. **Check the sensor label/sticker** for the correct APP KEY
3. **Some sensors need programming** - check manufacturer documentation for default keys

### Understanding TTN Event Messages

Here's what different TTN messages mean:

- **`"mic_mismatch"`** ❌: APP KEY doesn't match between sensor and TTN registration
- **`"join_cluster_fail"`** ❌: Usually caused by mic_mismatch (wrong APP KEY)
- **`"ns.down.transmission.success"`** ✅: TTN successfully sent downlink to device
- **`"ns.up.join.accept"`** ✅: Device successfully joined the network

### SE01-LB Sensor Specifics

For the specific SE01-LB soil sensor:

- **DEV EUI**: Usually on the sensor label (e.g., `A8404187D55BBA3B`)
- **SN**: Serial number on label (e.g., `LA6660...`)
- **APP EUI**: Check DRAGINO logs for what the sensor actually sends
- **Transmission intervals**: Expect data every 10-30 minutes to conserve battery

## Expected Results

Once everything is working correctly:

- **SYS LED**: Solid blue (connected to LoRaWAN server)
- **LoRa LED**: Blinks green when receiving sensor data
- **TTN Console**: Shows "Connected" status and regular sensor data
- **Sensor readings**: Appear in TTN's "Live data" tab with soil moisture, temperature, and battery levels

## Next Steps

With your LoRaWAN gateway successfully connected and sensors transmitting data, you can now:

- Monitor real-time sensor data through TTN
- Set up data visualization dashboards
- Configure alerts for sensor thresholds
- Integrate the data into your own applications via TTN's API

This setup provides a robust foundation for monitoring soil conditions, agricultural applications, or any IoT project requiring long-range, low-power connectivity.

Remember: LoRaWAN is designed for efficiency, so don't worry if you see gaps in data transmission - your sensors are conserving battery by design. Focus on the successful connection indicators and the quality of the data when it does arrive.
