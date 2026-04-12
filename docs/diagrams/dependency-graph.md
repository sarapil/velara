# Velara — Dependency Graph
# فيلارا — مخطط التبعيات

```mermaid
graph TD
    frappe["frappe v16"]
    erpnext["erpnext"]
    hrms["hrms"]
    frappe_visual["frappe_visual"]
    velara["Velara"]
    frappe --> velara
    erpnext --> velara
    hrms --> velara
    frappe_visual --> velara
    style velara fill:#C9A84C,color:#fff
    style frappe fill:#0089FF,color:#fff
```
