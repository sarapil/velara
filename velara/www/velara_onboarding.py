# Copyright (c) 2024, Arkan Lab and contributors
import frappe


def get_context(context):
    context.no_cache = 1
    context.title = frappe._("VELARA Onboarding")
    context.parents = [{"name": frappe._("Home"), "route": "/"}]
