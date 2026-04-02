# 🔗 Velara — Integrations Guide

> **Domain:** Hotel & Hospitality Management
> **Prefix:** VL

---

## Integration Map

```
Velara
  ├── ERPNext
  ├── HRMS
  ├── CAPS
  ├── frappe_visual
  ├── Arrowz
```

---

## ERPNext

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Velara | ERPNext | On submit | Document data |
| ERPNext | Velara | On change | Updated data |

### Configuration
```python
# In VL Settings or site_config.json
# erpnext_enabled = 1
```

---

## HRMS

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Velara | HRMS | On submit | Document data |
| HRMS | Velara | On change | Updated data |

### Configuration
```python
# In VL Settings or site_config.json
# hrms_enabled = 1
```

---

## CAPS

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Velara | CAPS | On submit | Document data |
| CAPS | Velara | On change | Updated data |

### Configuration
```python
# In VL Settings or site_config.json
# caps_enabled = 1
```

---

## frappe_visual

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Velara | frappe_visual | On submit | Document data |
| frappe_visual | Velara | On change | Updated data |

### Configuration
```python
# In VL Settings or site_config.json
# frappe_visual_enabled = 1
```

---

## Arrowz

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Velara | Arrowz | On submit | Document data |
| Arrowz | Velara | On change | Updated data |

### Configuration
```python
# In VL Settings or site_config.json
# arrowz_enabled = 1
```

---

## API Endpoints

All integration APIs use the standard response format from `velara.api.response`:

```python
from velara.api.response import success, error

@frappe.whitelist()
def sync_data():
    return success(data={}, message="Sync completed")
```

---

*Part of Velara by Arkan Lab*
