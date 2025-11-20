# Integration Guide for Auto-Update Feature

## File Created: update_ui_helper.py

Modular helper file dengan standalone functions untuk auto-update UI.

## How to Integrate

### Step 1: Add Import (Line 22)

```python
from db_manager import get_db
from update_ui_helper import create_update_button  # Add this line
```

### Step 2: Add Update Button in Header (Line ~1068)

Di method `_build_ui()`, cari bagian "# Company info and logout" dan tambahkan update button:

**BEFORE:**
```python
# Company info and logout
ft.Row([
    ft.Icon(ft.Icons.BUSINESS, color=RSM_BLUE, size=20),
    ft.Text(
        self.company_name,
        size=13,
        weight=ft.FontWeight.W_500,
        color=RSM_GREY,
    ),
    ft.Container(width=16),
    ft.OutlinedButton(
        "Logout",
        icon=ft.Icons.LOGOUT,
        on_click=self.handle_logout,
        style=ft.ButtonStyle(
            color=RSM_GREY,
        ),
        height=36,
    ),
], spacing=8),
```

**AFTER:**
```python
# Company info, update button, and logout
ft.Row([
    ft.Icon(ft.Icons.BUSINESS, color=RSM_BLUE, size=20),
    ft.Text(
        self.company_name,
        size=13,
        weight=ft.FontWeight.W_500,
        color=RSM_GREY,
    ),
    ft.Container(width=16),
    create_update_button(self),  # ADD THIS LINE
    ft.OutlinedButton(
        "Logout",
        icon=ft.Icons.LOGOUT,
        on_click=self.handle_logout,
        style=ft.ButtonStyle(
            color=RSM_GREY,
        ),
        height=36,
    ),
], spacing=8),
```

## That's It!

Hanya 2 perubahan minimal:
1. ✅ Import `create_update_button`
2. ✅ Tambahkan `create_update_button(self)` di header

Tidak perlu menambahkan method apapun ke class CoretaxExtractorApp!

## How It Works

- `update_ui_helper.py` berisi semua logic auto-update sebagai standalone functions
- `create_update_button(self)` membuat button yang sudah ter-wire ke update functions
- Semua functions menerima `app_instance` (self) sebagai parameter
- Clean separation of concerns - update logic terpisah dari main app

## Files Involved

- ✅ `update_ui_helper.py` - Update UI functions (NEW)
- ✅ `updater.py` - Update backend logic
- ✅ `version.json` - Version configuration
- ✅ `coretax_extractor_flet.py` - Main app (minimal changes)

## Test

```bash
uv run python coretax_extractor_flet.py
```

Login dan klik icon update (⟳) di header!
