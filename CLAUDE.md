# RegenNexus MCP Server

RegenNexus is a universal hardware-software-AI communication platform.

## When to Use

Use RegenNexus tools when the user wants to:
- Control hardware devices (GPIO pins, LEDs, motors)
- Operate robotic arms (move to positions, control gripper)
- Read sensor data (temperature, humidity, distance, light, pressure)
- List or query connected devices

## Available Tools (Free Tier)

| Tool | Description |
|------|-------------|
| `gpio_write` | Set a GPIO pin to HIGH (1) or LOW (0) |
| `robot_arm_move` | Move a robotic arm to specified joint positions |
| `gripper_control` | Open or close a robotic gripper |
| `read_sensor` | Read value from a sensor |
| `list_devices` | List all connected hardware devices |

## Usage Examples

### Control GPIO
```
Tool: gpio_write
Arguments: {"device_id": "raspi-001", "pin": 18, "value": 1}
```

### Move Robot Arm
```
Tool: robot_arm_move
Arguments: {
  "device_id": "arm-001",
  "positions": [0, 45, -30, 0, 60, 0, 0],
  "duration": 2.0
}
```

### Control Gripper
```
Tool: gripper_control
Arguments: {"device_id": "arm-001", "action": "close", "force": 10}
```

### Read Sensor
```
Tool: read_sensor
Arguments: {"device_id": "sensor-001", "sensor_type": "temperature"}
```

### List Devices
```
Tool: list_devices
Arguments: {}
```

## Best Practices

1. Use `list_devices` to discover available device IDs
2. For robotic arms, positions array should have 7 values for 7-DOF arms
3. Sensor types: temperature, humidity, distance, light, pressure
4. GPIO values: 0 = LOW, 1 = HIGH

## Error Handling

Tool responses include either:
- `{"success": true, ...}` for successful operations
- `{"error": "description"}` for failures

Always check response for errors before confirming success to user.
