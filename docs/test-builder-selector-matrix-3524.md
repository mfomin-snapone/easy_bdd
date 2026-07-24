# Test Builder Selector Variable Matrix - Suite 3524 Drafts

- Scope: strict-v2 hardened conversion drafts in Project 59, Suite 107622, Section 2890100
- Source suite lineage: 3524 benchmark conversion set
- Generated: 2026-07-24

Shared Var case:
- C18808614 - Var: Builder Strict V3 - Araknis Defaults
- Include this Var case in the run (Untested/Retest) so all Feature cases can resolve ${...} placeholders.

Working websocket shared cases (derived from C18690483 and C18690468):
- C18808615 - Shared: OvrC dxGetAbout Working
- C18808616 - Shared: OvrC Firmware Upgrade Working
- Include these when composing Feature cases with shared_step references for OvrC GET/POST flows.

This matrix lists the selector and runtime variables required to execute the 20 hardened draft cases with minimal manual edits.
The strict-v4 set now follows the UI interaction rhythm proven in C18738087: login, wait-for-ready,
edit flow, save, pending-change verification, apply, and post-apply checks.
For Linux shell execution, these drafts now force `headless: true` and call
`Shared: OvrC dxGetAbout Working` instead of inline websocket payloads.

## Global Runtime Variables (all 20 cases)

- ${device_url}
- ${device_api_url}
- ${ws_url}
- ${save_selector}
- ${settle_seconds}

## Case Family Variable Profiles

| Family | Required variables |
|---|---|
| System Name | ${system_name_selector}, ${system_name_value}, ${system_name_display_selector} |
| Admin Username | ${admin_username_selector}, ${admin_username_value}, ${admin_username_display_selector} |
| Admin Password | ${current_password_selector}, ${current_password}, ${new_password_selector}, ${new_password}, ${confirm_password_selector}, ${password_update_success_text} |
| Management VLAN | ${management_vlan_mode_selector}, ${management_vlan_mode}, ${management_vlan_id_selector}, ${management_vlan_id}, ${ui_success_text} |
| Date and Time Settings | ${date_input_selector}, ${date_value}, ${time_input_selector}, ${time_value}, ${datetime_display_selector} |
| Time Zone | ${timezone_selector}, ${timezone_value}, ${daylight_savings_toggle_selector}, ${timezone_display_selector} |
| IP Settings > DHCP | ${ip_mode_selector}, ${ip_mode_display_selector} |
| IP Settings > Static | ${ip_mode_selector}, ${ip_address_selector}, ${static_ip}, ${subnet_selector}, ${static_subnet}, ${gateway_selector}, ${static_gateway}, ${primary_dns_selector}, ${static_dns_primary}, ${ip_address_display_selector} |
| Interface Settings | ${lan_port_selector}, ${lan_port}, ${speed_selector}, ${speed_value}, ${duplex_selector}, ${duplex_value}, ${ui_success_text} |
| WAP Mode | ${wap_mode_selector}, ${wap_mode_value}, ${mode_display_selector} |
| Fast Roaming | ${fast_roaming_toggle_selector}, ${ui_success_text} |
| Networks > SSID | ${ssid_name_selector}, ${ssid_name}, ${ssid_security_selector}, ${ssid_security_mode}, ${ssid_band_selector}, ${ssid_band}, ${ssid_broadcast_toggle_selector}, ${ssid_display_selector} |
| Guest Network | ${guest_ssid_selector}, ${guest_ssid_name}, ${guest_security_mode_selector}, ${guest_security_mode}, ${guest_band_selector}, ${guest_band}, ${guest_broadcast_toggle_selector}, ${guest_ssid_display_selector} |

## Case-to-Family Mapping

| TestRail case | Title | Family |
|---|---|---|
| C18808593 | System Name | System Name |
| C18808594 | Admin Username | Admin Username |
| C18808595 | Admin Password | Admin Password |
| C18808596 | Management VLAN | Management VLAN |
| C18808597 | Date and Time Settings | Date and Time Settings |
| C18808598 | Time Zone | Time Zone |
| C18808599 | IP Settings > DHCP | IP Settings > DHCP |
| C18808600 | IP Settings > Static | IP Settings > Static |
| C18808601 | Interface Settings | Interface Settings |
| C18808602 | WAP Mode | WAP Mode |
| C18808603 | Utilization of SSID > Fast Roaming | Fast Roaming |
| C18808604 | Networks > SSID 1-8 > 2.4 > Open | Networks > SSID |
| C18808605 | Networks > SSID 1-8 > 2.4 >WPA2-PSK | Networks > SSID |
| C18808606 | Networks > SSID 1-8 > 5 > Open | Networks > SSID |
| C18808607 | Networks > SSID 1-8 > 5 > WPA2-PSK | Networks > SSID |
| C18808608 | Networks > SSID 1-8 > Both > Open | Networks > SSID |
| C18808609 | Networks > SSID 1-8 > Both > WPA2-PSK | Networks > SSID |
| C18808610 | Guest Network > SSID 1 > 2.4 > Open | Guest Network |
| C18808611 | Guest Network > SSID 1 > 2.4 > WPA2-PSK | Guest Network |
| C18808612 | Guest Network > SSID 2 > 5 > Open | Guest Network |

## Suggested Defaults for Faster Bring-up

- ${settle_seconds}: 15
- ${ws_url}: ws://${device_host}/ws
- ${device_api_url}: http://${device_host}/api
- ${ui_success_text}: Saved
- ${ssid_security_mode}: WPA2-PSK or Open per case title
- ${ssid_band}: 2.4, 5, or both per case title
- ${guest_security_mode}: WPA2-PSK or Open per case title
- ${guest_band}: 2.4 or 5 per case title

## Notes

- All strict-v2 cases include baseline and post-action cross-channel checks using websocket and local API.
- Keep selector values product/firmware specific; names here are normalized placeholders for repeatable mapping.
