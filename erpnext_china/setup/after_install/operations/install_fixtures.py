import json
import os
import warnings
from pathlib import Path

import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def install(country="China"):
    frappe.db.set_default("date_format", "yyyy-mm-dd")

    records = [
        {
            "doctype": "Territory",
            "territory_name": _("All Territories"),
            "is_group": 1,
            "name": _("All Territories"),
            "parent_territory": "",
        }
    ]

    import csv
    with open((Path(__file__).parent.parent / "data" / "territory.csv"), mode="rt", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for line in reader:
            records.append({
                "doctype": "Territory",
                "territory_name": _(line["区域名称"]),
                "is_group": int(line["是否群组"]),
                "parent_territory": _(line["上级区域"]),
            })

    make_records(records)
    overwrite_workspace()


def overwrite_workspace():
    apps_dir = Path(__file__).parent.parent.parent.parent.parent.parent
    workspace_files = []
    for app in ["frappe", "erpnext"]:
        app_dir = apps_dir / app
        if app_dir.exists():
            for json_file in app_dir.rglob("workspace/*.json"):
                workspace_files.append(json_file)

    for file_path in workspace_files:
        try:
            save_workspace_blocks(file_path)
        except Exception as e:
            warnings.warn(f"跳过 {file_path.name}: {e}", Warning)


def save_workspace_blocks(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    updated_content = file_content \
        .replace("<b>Your Shortcuts</b>", "<b>快捷入口</b>") \
        .replace("<b>Reports &amp; Masters</b>", "<b>功能&报表</b>") \
        .replace("<b>Quick Access</b>", "<b>快捷入口</b>") \
        .replace("<b>Masters & Reports</b>", "<b>功能&报表</b>")

    data = json.loads(updated_content)
    args = {
        "title": data["title"],
        "public": data["public"],
        "new_widgets": json.dumps({}),
        "blocks": data.get("content", [])
    }

    try:
        frappe.call("frappe.desk.doctype.workspace.workspace.save_page", **args)
    except frappe.exceptions.LinkValidationError as e:
        warnings.warn(str(e), Warning)
