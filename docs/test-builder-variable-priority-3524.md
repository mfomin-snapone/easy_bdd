# Variable Priority Manifest - Strict-v2 Draft Cases

- Scope: Project 59, Suite 107622, Section 2890100
- Cases covered: 20 (C18808593-C18808612)
- Method: frequency across case preconditions + local .env key presence check
- Generated: 2026-07-24

## Priority 0 (Blockers across all 20 cases)

These must be filled first.

- device_url (used by 20, currently missing)
- device_api_url (used by 20, currently missing)
- ws_url (used by 20, currently missing)
- save_selector (used by 20, currently missing)
- settle_seconds (used by 20, currently missing)

## Priority 1 (Affects largest subsets)

- ssid_name_selector (used by 6, missing)
- ssid_name (used by 6, missing)
- ssid_security_selector (used by 6, missing)
- ssid_security_mode (used by 6, missing)
- ssid_band_selector (used by 6, missing)
- ssid_band (used by 6, missing)
- ssid_broadcast_toggle_selector (used by 6, missing)
- ssid_display_selector (used by 6, missing)

## Priority 2 (Guest network block)

- guest_ssid_selector (used by 3, missing)
- guest_ssid_name (used by 3, missing)
- guest_security_mode_selector (used by 3, missing)
- guest_security_mode (used by 3, missing)
- guest_band_selector (used by 3, missing)
- guest_band (used by 3, missing)
- guest_broadcast_toggle_selector (used by 3, missing)
- guest_ssid_display_selector (used by 3, missing)
- ui_success_text (used by 3, missing)

## Priority 3 (Dual-case modules)

- ip_mode_selector (used by 2, missing)

## Priority 4 (Single-case families)

### System Name
- system_name_selector
- system_name_value
- system_name_display_selector

### Admin Username
- admin_username_selector
- admin_username_value
- admin_username_display_selector

### Admin Password
- current_password_selector
- current_password
- new_password_selector
- new_password
- confirm_password_selector
- password_update_success_text

### Management VLAN
- management_vlan_mode_selector
- management_vlan_mode
- management_vlan_id_selector
- management_vlan_id

### Date and Time Settings
- date_input_selector
- date_value
- time_input_selector
- time_value
- datetime_display_selector

### Time Zone
- timezone_selector
- timezone_value
- daylight_savings_toggle_selector
- timezone_display_selector

### IP Settings DHCP
- ip_mode_display_selector

### IP Settings Static
- ip_address_selector
- static_ip
- subnet_selector
- static_subnet
- gateway_selector
- static_gateway
- primary_dns_selector
- static_dns_primary
- ip_address_display_selector

### Interface Settings
- lan_port_selector
- lan_port
- speed_selector
- speed_value
- duplex_selector
- duplex_value

### WAP Mode
- wap_mode_selector
- wap_mode_value
- mode_display_selector

### Fast Roaming
- fast_roaming_toggle_selector

## Operational note

Your local .env currently has none of the strict-v2 case variables above defined by key name. Use [test-builder-variable-template-3524.env.example](./test-builder-variable-template-3524.env.example) as the fastest fill-in path.
