# Test Builder Conversion Benchmark - Suite 3524 (Sample 20)

- Source suite: `3524` (Project `50`)
- Cases sampled: `20`
- Generated on: `2026-07-24`

This benchmark maps manual TestRail steps (`custom_steps_separated`) into draft EasyBDD Feature templates suitable for Builder AI prompt tuning and human review.

## 1. C1631412 - System Name

- Manual step count: `2`
- Step sample 1: `Positive Case Enter: Test!@$-_123`
- Step sample 2: `Negative Case Enter: Test!@$-_123^&*(`

Draft EasyBDD template:
```yaml
Feature: System Name
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631412 converted from manual steps"
- test.log:
    message: "Step 1 intent: Positive Case Enter: Test!@$-_123"
- test.assert:
    expression: "true"
    message: "Expected: Accepts: Test!@$-_123"
- test.log:
    message: "Step 2 intent: Negative Case Enter: Test!@$-_123^&*("
- test.assert:
    expression: "true"
    message: "Expected: Errors: System Name: # , ' , " , : , ; , \ , / , [ , & , + , `, (comma),(Space) are Invalid characters"
```

## 2. C1631413 - Admin Username

- Manual step count: `2`
- Step sample 1: `Positive Case Enter: Test_User 123!@#$%^&*`
- Step sample 2: `Negative Case Enter: *Leave Blank*`

Draft EasyBDD template:
```yaml
Feature: Admin Username
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631413 converted from manual steps"
- test.log:
    message: "Step 1 intent: Positive Case Enter: Test_User 123!@#$%^&*"
- test.assert:
    expression: "true"
    message: "Expected: Accepts: Test_User 123!@#$%^&*"
- test.log:
    message: "Step 2 intent: Negative Case Enter: *Leave Blank*"
- test.assert:
    expression: "true"
    message: "Expected: Errors: Name: Length must between 1 and 32!!"
```

## 3. C1631414 - Admin Password

- Manual step count: `6`
- Step sample 1: `Check that the current password field accepts the correct password. Current Password = SnapAV704 Test - SnapAV704`
- Step sample 2: `Check that the current password field and validate that it does not accept an incorrect password. Current Password = SnapAV704 Test - SnapAV704!`

Draft EasyBDD template:
```yaml
Feature: Admin Password
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631414 converted from manual steps"
- test.log:
    message: "Step 1 intent: Check that the current password field accepts the correct password. Current Password = SnapAV704 Test - SnapAV704"
- test.assert:
    expression: "true"
    message: "Expected: Accepts the current password as its correct. Allows the setting of the new password as tested below. No errors"
- test.log:
    message: "Step 2 intent: Check that the current password field and validate that it does not accept an incorrect password. Current Password = SnapAV704 Test - SnapAV704!"
- test.assert:
    expression: "true"
    message: "Expected: Error: "Invalid Current Password !""
```

## 4. C1631416 - Management VLAN

- Manual step count: `2`
- Step sample 1: `Untagged`
- Step sample 2: `Tagged`

Draft EasyBDD template:
```yaml
Feature: Management VLAN
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631416 converted from manual steps"
- test.log:
    message: "Step 1 intent: Untagged"
- test.assert:
    expression: "true"
    message: "Expected: Default state out of the box. Will connect to any subnet and allow UI access"
- test.log:
    message: "Step 2 intent: Tagged"
- test.assert:
    expression: "true"
    message: "Expected: Use a VLAN tag value up to 4096, Only this assigned subnet value will allow access to the ap's local UI  This requires prior configuration on the core network for this feature to p"
```

## 5. C1631418 - Date and Time Settings

- Manual step count: `7`
- Step sample 1: `Manually Set Date and Time feature, Test all combinations of time settings. Enter the current days time and date: 2020/07/16 14:16 (2:16)`
- Step sample 2: `Manually Set Date and Time feature, Test all combinations of time settings. Enter the incorrect days time and date: 2020/96/16 14:16 (2:16)`

Draft EasyBDD template:
```yaml
Feature: Date and Time Settings
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631418 converted from manual steps"
- test.log:
    message: "Step 1 intent: Manually Set Date and Time feature, Test all combinations of time settings. Enter the current days time and date: 2020/07/16 14:16 (2:16)"
- test.assert:
    expression: "true"
    message: "Expected: Time should display correctly based on the user settings in the local UI of the ap"
- test.log:
    message: "Step 2 intent: Manually Set Date and Time feature, Test all combinations of time settings. Enter the incorrect days time and date: 2020/96/16 14:16 (2:16)"
- test.assert:
    expression: "true"
    message: "Expected: Error: Invalid value of month."
```

## 6. C1631419 - Time Zone

- Manual step count: `3`
- Step sample 1: `Test different timezones from the timezone drop-down, validate the time adjusts accordingly in the UI when a selected timezone was adjusted from the local zone you are currently in`
- Step sample 2: `Enable/Disable Toggle for Daylight Savings`

Draft EasyBDD template:
```yaml
Feature: Time Zone
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631419 converted from manual steps"
- test.log:
    message: "Step 1 intent: Test different timezones from the timezone drop-down, validate the time adjusts accordingly in the UI when a selected timezone was adjusted from the local zone you are currently in"
- test.assert:
    expression: "true"
    message: "Expected: Each time zone approprioately adjust depending on the zone selected"
- test.log:
    message: "Step 2 intent: Enable/Disable Toggle for Daylight Savings"
- test.assert:
    expression: "true"
    message: "Expected: Enables daylight savings for the zones that practice daylight savings. Enables the schedule function"
```

## 7. C1631427 - IP Settings > DHCP

- Manual step count: `1`
- Step sample 1: `Set the AP to DHCP`

Draft EasyBDD template:
```yaml
Feature: IP Settings > DHCP
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631427 converted from manual steps"
- test.log:
    message: "Step 1 intent: Set the AP to DHCP"
- test.assert:
    expression: "true"
    message: "Expected: A DHCP server dynamically assigns an IP address and other network configuration parameters to AP  Make sure the AP is accessible by that IP address"
```

## 8. C1631428 - IP Settings > Static

- Manual step count: `2`
- Step sample 1: `Set the AP to Static populating all fields, IP address, Subnet Mask, Default Gateway, Primary DNS, Secondary DNS  Settings before save/apply 192.168.1.50 255.255.255.0 192.168.1.1 `
- Step sample 2: `Set the AP to Static populating all fields incorrectly, IP address, Subnet Mask, Default Gateway, Primary DNS, Secondary DNS.   Settings before save/apply 192.168.460.460 255.255.2`

Draft EasyBDD template:
```yaml
Feature: IP Settings > Static
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631428 converted from manual steps"
- test.log:
    message: "Step 1 intent: Set the AP to Static populating all fields, IP address, Subnet Mask, Default Gateway, Primary DNS, Secondary DNS  Settings before save/apply 192.168.1.50 255.255.255.0 192.168.1.1 "
- test.assert:
    expression: "true"
    message: "Expected: Once settings are saved and applied, the AP should be set to a static IP of 192.168.1.50  All settings should result in: 192.168.1.50 255.255.255.0 192.168.1.1 1.1.1.1 8.8.8.8  Mak"
- test.log:
    message: "Step 2 intent: Set the AP to Static populating all fields incorrectly, IP address, Subnet Mask, Default Gateway, Primary DNS, Secondary DNS.   Settings before save/apply 192.168.460.460 255.255.2"
- test.assert:
    expression: "true"
    message: "Expected: Error: The IPv4 Address is an invalid format"
```

## 9. C1631429 - Interface Settings

- Manual step count: `1`
- Step sample 1: `Set interface settings to a combination of the options listed in the dropdowns. Then test the interface speed to validate that settings are correct.  Duplex can be determined throu`

Draft EasyBDD template:
```yaml
Feature: Interface Settings
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631429 converted from manual steps"
- test.log:
    message: "Step 1 intent: Set interface settings to a combination of the options listed in the dropdowns. Then test the interface speed to validate that settings are correct.  Duplex can be determined throu"
- test.assert:
    expression: "true"
    message: "Expected: E.g. 1 LAN1 - 10Mbps - Speedtest will result in speeds of 10Mbps or less through the wireless network  E.g. 2 LAN1 - Disabled - No communication to the AP from the network which wi"
```

## 10. C1631438 - WAP Mode

- Manual step count: `3`
- Step sample 1: `Standalone Mode`
- Step sample 2: `Mesh > Controller`

Draft EasyBDD template:
```yaml
Feature: WAP Mode
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631438 converted from manual steps"
- test.log:
    message: "Step 1 intent: Standalone Mode"
- test.assert:
    expression: "true"
    message: "Expected: The AP's UI should represent the functionality of the standard wireless access point mode. Features utilized by Standalone mode should be present in the UI of the AP. It should fun"
- test.log:
    message: "Step 2 intent: Mesh > Controller"
- test.assert:
    expression: "true"
    message: "Expected: The AP's UI should represent the functionality of the Mesh Controller mode. Features utilized by Mesh Controller mode should be present in the UI of the AP. It should function as a"
```

## 11. C1631437 - Utilization of SSID > Fast Roaming

- Manual step count: `2`
- Step sample 1: `Fast Roaming Enabled`
- Step sample 2: `Fast Roaming Disabled`

Draft EasyBDD template:
```yaml
Feature: Utilization of SSID > Fast Roaming
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631437 converted from manual steps"
- test.log:
    message: "Step 1 intent: Fast Roaming Enabled"
- test.assert:
    expression: "true"
    message: "Expected: Enables seamless roaming between ap's using the same SSID's"
- test.log:
    message: "Step 2 intent: Fast Roaming Disabled"
- test.assert:
    expression: "true"
    message: "Expected: Disables seamless roaming between ap's using the same SSID's"
```

## 12. C1631439 - Networks > SSID 1-8 > 2.4 > Open

- Manual step count: `2`
- Step sample 1: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled - Client Isolat`
- Step sample 2: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disabled - Client Isola`

Draft EasyBDD template:
```yaml
Feature: Networks > SSID 1-8 > 2.4 > Open
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631439 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled - Client Isolat"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to Open, connect a client without a password, verify internet through each SSID on the 2.4 channel - You should"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disabled - Client Isola"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to Open, connect a client without a password, verify internet through each SSID on the 2.4 channel - You will n"
```

## 13. C1631440 - Networks > SSID 1-8 > 2.4 >WPA2-PSK

- Manual step count: `3`
- Step sample 1: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK    - Encryption is Default   - Enter a Passphrase "SnapAV704!@"   - Gro`
- Step sample 2: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK    - Encryption is Default   - Enter a Passphrase "SnapAV704!@"   - Gro`

Draft EasyBDD template:
```yaml
Feature: Networks > SSID 1-8 > 2.4 >WPA2-PSK
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631440 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK    - Encryption is Default   - Enter a Passphrase "SnapAV704!@"   - Gro"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to WPA2-PSK, connect a client with the set password, verify internet through each SSID on the 2.4 channel - Gro"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK    - Encryption is Default   - Enter a Passphrase "SnapAV704!@"   - Gro"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to WPA2-PSK, connect a client with the set password, verify internet through each SSID on the 2.4 channel - Gro"
```

## 14. C1631441 - Networks > SSID 1-8 > 5 > Open

- Manual step count: `2`
- Step sample 1: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled - Client Isolat`
- Step sample 2: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disabled - Client Isola`

Draft EasyBDD template:
```yaml
Feature: Networks > SSID 1-8 > 5 > Open
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631441 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled - Client Isolat"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to Open, connect a client without a password, verify internet through each SSID on the 5 channel - You should s"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disabled - Client Isola"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to Open, connect a client without a password, verify internet through each SSID on the 5 channel - You will not"
```

## 15. C1631442 - Networks > SSID 1-8 > 5 > WPA2-PSK

- Manual step count: `3`
- Step sample 1: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey "`
- Step sample 2: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey "`

Draft EasyBDD template:
```yaml
Feature: Networks > SSID 1-8 > 5 > WPA2-PSK
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631442 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey ""
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to WPA2-PSK, connect a client with the set password, verify internet through each SSID on the 5 channel - Group"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey ""
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to WPA2-PSK, connect a client with the set password, verify internet through each SSID on the 5 channel - Group"
```

## 16. C1631450 - Networks > SSID 1-8 > Both > Open

- Manual step count: `2`
- Step sample 1: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled - Client Isolat`
- Step sample 2: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disabled - Client Isola`

Draft EasyBDD template:
```yaml
Feature: Networks > SSID 1-8 > Both > Open
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631450 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled - Client Isolat"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to Open, connect a client without a password, verify internet through each SSID on both channels (2.4 & 5) - Yo"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disabled - Client Isola"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to Open, connect a client without a password, verify internet through each SSID on both channels (2.4 & 5) - Yo"
```

## 17. C1631451 - Networks > SSID 1-8 > Both > WPA2-PSK

- Manual step count: `3`
- Step sample 1: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey "`
- Step sample 2: `Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey "`

Draft EasyBDD template:
```yaml
Feature: Networks > SSID 1-8 > Both > WPA2-PSK
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631451 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey ""
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to WPA2-PSK, connect a client with the set password, verify internet through each SSID on both channels (2.4 & "
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable SSID field 1-8, Name SSID 1-8; Test1-Test8 - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704!@" - Groupkey ""
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as Test1-Test8 - Wireless security is set to WPA2-PSK, connect a client with the set password, verify internet through each SSID on both channels (2.4 & "
```

## 18. C1631444 - Guest Network > SSID 1 > 2.4 > Open

- Manual step count: `2`
- Step sample 1: `Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled`
- Step sample 2: `Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disable`

Draft EasyBDD template:
```yaml
Feature: Guest Network > SSID 1 > 2.4 > Open
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631444 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as GuestNetwork - Wireless security is set to Open, connect a client without a password, verify internet through the SSID on the 2.4 channel - You should"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disable"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as GuestNetwork - Wireless security is set to Open, connect a client without a password, verify internet through the SSID on the 2.4 channel - You will n"
```

## 19. C1631445 - Guest Network > SSID 1 > 2.4 > WPA2-PSK

- Manual step count: `2`
- Step sample 1: `Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704`
- Step sample 2: `Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704`

Draft EasyBDD template:
```yaml
Feature: Guest Network > SSID 1 > 2.4 > WPA2-PSK
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631445 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as GuestNetwork - Wireless security is set to Open, connect a client without a password, verify internet through the SSID on the 2.4 channel - Groupkey s"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - WPA2-PSK - Encryption is Default - Enter a Passphrase "SnapAV704"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as GuestNetwork - Wireless security is set to Open, connect a client without a password, verify internet through the SSID on the 2.4 channel - Groupkey s"
```

## 20. C1631446 - Guest Network > SSID 2 > 5 > Open

- Manual step count: `2`
- Step sample 1: `Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled`
- Step sample 2: `Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disable`

Draft EasyBDD template:
```yaml
Feature: Guest Network > SSID 2 > 5 > Open
- browser.open:
    url: ${device_url}
- test.log:
    message: "Case C1631446 converted from manual steps"
- test.log:
    message: "Step 1 intent: Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Enabled"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as GuestNetwork - Wireless security is set to Open, connect a client without a password, verify internet through the SSID on the 5 channel - You should s"
- test.log:
    message: "Step 2 intent: Configure as described below: - Enable Guest Network SSID, Name Guest Network SSID - GuestNetwork - Security Mode - Open - Select Save in the pop-up window - Broadcast SSID Disable"
- test.assert:
    expression: "true"
    message: "Expected: Output: - SSID should show as GuestNetwork - Wireless security is set to Open, connect a client without a password, verify internet through the SSID on the 5 channel - You will not"
```


## Published Draft Batch (Project 59)

Published to suite `107622` section `2890100` for review-only validation.

Created draft cases:
- C18808593 from C1631412
- C18808594 from C1631413
- C18808595 from C1631414
- C18808596 from C1631416
- C18808597 from C1631418
- C18808598 from C1631419
- C18808599 from C1631427
- C18808600 from C1631428
- C18808601 from C1631429
- C18808602 from C1631438

Notes:
- These are intentionally marked with automation status TODO (`custom_automation_status=1`).
- Each case is a conversion draft and includes explicit placeholder assertions requiring engineer review before execution.


## Review Priority Score (1-5)

Higher score means more complex/risk-prone manual scenario; review these drafts first.

| Benchmark # | Source Case | Title | Manual Steps | Priority Score |
|---|---:|---|---:|---:|
| 1 | C1631412 | System Name | 2 | 1 |\n| 2 | C1631413 | Admin Username | 2 | 2 |\n| 3 | C1631414 | Admin Password | 6 | 4 |\n| 4 | C1631416 | Management VLAN | 2 | 1 |\n| 5 | C1631418 | Date and Time Settings | 7 | 3 |\n| 6 | C1631419 | Time Zone | 3 | 2 |\n| 7 | C1631427 | IP Settings > DHCP | 1 | 1 |\n| 8 | C1631428 | IP Settings > Static | 2 | 1 |\n| 9 | C1631429 | Interface Settings | 1 | 1 |\n| 10 | C1631438 | WAP Mode | 3 | 1 |\n| 11 | C1631437 | Utilization of SSID > Fast Roaming | 2 | 1 |\n| 12 | C1631439 | Networks > SSID 1-8 > 2.4 > Open | 2 | 3 |\n| 13 | C1631440 | Networks > SSID 1-8 > 2.4 >WPA2-PSK | 3 | 3 |\n| 14 | C1631441 | Networks > SSID 1-8 > 5 > Open | 2 | 3 |\n| 15 | C1631442 | Networks > SSID 1-8 > 5 > WPA2-PSK | 3 | 3 |\n| 16 | C1631450 | Networks > SSID 1-8 > Both > Open | 2 | 3 |\n| 17 | C1631451 | Networks > SSID 1-8 > Both > WPA2-PSK | 3 | 3 |\n| 18 | C1631444 | Guest Network > SSID 1 > 2.4 > Open | 2 | 3 |\n| 19 | C1631445 | Guest Network > SSID 1 > 2.4 > WPA2-PSK | 2 | 3 |\n| 20 | C1631446 | Guest Network > SSID 2 > 5 > Open | 2 | 3 |\n