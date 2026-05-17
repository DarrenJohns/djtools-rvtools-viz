"""Normalize raw Azure Disk SKU data into a clean JSON format."""
import json
import sys
from datetime import datetime

if len(sys.argv) != 4:
    print("Usage: normalize-disks.py <raw-file> <output-file> <region-display-name>")
    sys.exit(1)

raw_file = sys.argv[1]
output_file = sys.argv[2]
display_name = sys.argv[3]

with open(raw_file, encoding='utf-8') as f:
    raw = json.load(f)

region_name = raw_file.replace('\\', '/').rsplit('/', 1)[-1].replace('-disks-raw.json', '')


def get_cap(caps, name):
    for c in caps:
        if c['name'] == name:
            return c['value']
    return None


def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


# Disk tier display names
TIER_LABELS = {
    'Premium_LRS': 'Premium SSD',
    'Premium_ZRS': 'Premium SSD (ZRS)',
    'PremiumV2_LRS': 'Premium SSD v2',
    'StandardSSD_LRS': 'Standard SSD',
    'StandardSSD_ZRS': 'Standard SSD (ZRS)',
    'Standard_LRS': 'Standard HDD',
    'UltraSSD_LRS': 'Ultra Disk',
}

disks = []
for item in raw:
    if item.get('resourceType') != 'disks':
        continue
    caps = item.get('capabilities', [])
    loc_info = item.get('locationInfo', [{}])[0] if item.get('locationInfo') else {}
    zones = sorted(loc_info.get('zones', []))
    restrictions = item.get('restrictions', [])
    restriction_reasons = [r.get('reasonCode', '') for r in restrictions] if restrictions else []

    name = item.get('name', '')
    size = item.get('size', '')
    tier = item.get('tier', '')

    # Skip type-level entries (no specific size like "P" or "U")
    if size in ('P', 'U', 'E', 'S'):
        continue

    disk = {
        'name': name,
        'size': size,
        'tier': tier,
        'tierLabel': TIER_LABELS.get(name, name),
        'maxSizeGiB': safe_int(get_cap(caps, 'MaxSizeGiB')),
        'minSizeGiB': safe_int(get_cap(caps, 'MinSizeGiB')),
        'maxIOPS': safe_int(get_cap(caps, 'MaxIOps') or get_cap(caps, 'MaxIOpsReadWrite')),
        'maxThroughputMBps': safe_float(get_cap(caps, 'MaxBandwidthMBps') or get_cap(caps, 'MaxBandwidthMBpsReadWrite')),
        'maxShares': safe_int(get_cap(caps, 'MaxValueOfMaxShares')),
        'burstIOPS': safe_int(get_cap(caps, 'MaxBurstIops')),
        'burstThroughputMBps': safe_float(get_cap(caps, 'MaxBurstBandwidthMBps')),
        'zones': zones,
        'restrictions': restriction_reasons,
    }
    disks.append(disk)

# Sort by tier then by size number
def size_sort_key(d):
    import re
    num = re.search(r'\d+', d['size'])
    return (d['name'], int(num.group()) if num else 0)

disks.sort(key=size_sort_key)

output = {
    'region': region_name,
    'regionDisplayName': display_name,
    'lastUpdated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'diskCount': len(disks),
    'disks': disks
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f'  Normalized {len(disks)} disk SKUs')
