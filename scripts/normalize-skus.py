"""Normalize raw Azure VM SKU data into a clean JSON format."""
import json
import sys
from datetime import datetime

if len(sys.argv) != 4:
    print("Usage: normalize-skus.py <raw-file> <output-file> <region-display-name>")
    sys.exit(1)

raw_file = sys.argv[1]
output_file = sys.argv[2]
display_name = sys.argv[3]

with open(raw_file, encoding='utf-8') as f:
    raw = json.load(f)

# Extract region name from the raw filename
region_name = raw_file.replace('\\', '/').rsplit('/', 1)[-1].replace('-raw.json', '')


def get_cap(caps, name):
    for c in caps:
        if c['name'] == name:
            return c['value']
    return None


skus = []
for item in raw:
    if item.get('resourceType') != 'virtualMachines':
        continue
    caps = item.get('capabilities', [])
    loc_info = item.get('locationInfo', [{}])[0] if item.get('locationInfo') else {}
    zones = sorted(loc_info.get('zones', []))
    restrictions = item.get('restrictions', [])
    restriction_reasons = [r.get('reasonCode', '') for r in restrictions] if restrictions else []
    skus.append({
        'name': item['name'],
        'family': item.get('family', ''),
        'tier': item.get('tier', ''),
        'size': item.get('size', ''),
        'vCPUs': int(get_cap(caps, 'vCPUs') or 0),
        'memoryGB': float(get_cap(caps, 'MemoryGB') or 0),
        'maxDataDisks': int(get_cap(caps, 'MaxDataDiskCount') or 0),
        'maxNICs': int(get_cap(caps, 'MaxNetworkInterfaces') or 0),
        'cpuArchitecture': get_cap(caps, 'CpuArchitectureType') or 'x64',
        'hyperVGenerations': get_cap(caps, 'HyperVGenerations') or '',
        'acceleratedNetworking': get_cap(caps, 'AcceleratedNetworkingEnabled') == 'True',
        'premiumIO': get_cap(caps, 'PremiumIO') == 'True',
        'ephemeralOSDisk': get_cap(caps, 'EphemeralOSDiskSupported') == 'True',
        'encryptionAtHost': get_cap(caps, 'EncryptionAtHostSupported') == 'True',
        'spotEligible': get_cap(caps, 'LowPriorityCapable') == 'True',
        'zones': zones,
        'restrictions': restriction_reasons
    })

skus.sort(key=lambda x: (x['family'], x['vCPUs'], x['memoryGB']))

output = {
    'region': region_name,
    'regionDisplayName': display_name,
    'lastUpdated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'skuCount': len(skus),
    'skus': skus
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f'  Normalized {len(skus)} SKUs')
