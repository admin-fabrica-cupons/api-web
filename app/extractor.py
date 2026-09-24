from __future__ import annotations

import json
from typing import Any

from bs4 import BeautifulSoup


def _meta_content(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str | None:
    attrs: dict[str, str] = {}
    if name:
        attrs["name"] = name
    if prop:
        attrs["property"] = prop
    tag = soup.find("meta", attrs=attrs)
    if tag and tag.get("content"):
        return str(tag.get("content")).strip()
    return None


def _first_product_jsonld(items: list[Any]) -> dict[str, Any] | None:
    def walk(value: Any):
        if isinstance(value, dict):
            value_type = value.get("@type")
            if value_type == "Product" or (isinstance(value_type, list) and "Product" in value_type):
                return value
            graph = value.get("@graph")
            if isinstance(graph, list):
                for entry in graph:
                    found = walk(entry)
                    if found:
                        return found
        elif isinstance(value, list):
            for entry in value:
                found = walk(entry)
                if found:
                    return found
        return None

    for item in items:
        found = walk(item)
        if found:
            return found
    return None


def _normalize_offer(offers: Any) -> dict[str, Any]:
    if isinstance(offers, list) and offers:
        offers = offers[0]
    if not isinstance(offers, dict):
        return {}
    return {
        "price": offers.get("price") or offers.get("lowPrice"),
        "currency": offers.get("priceCurrency"),
        "availability": offers.get("availability"),
        "url": offers.get("url"),
    }


def extract_page_data(html: str, final_url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else None
    canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical = canonical_tag.get("href") if canonical_tag else None

    json_ld: list[Any] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text()
        if not raw or not raw.strip():
            continue
        try:
            json_ld.append(json.loads(raw))
        except json.JSONDecodeError:
            continue

    product_ld = _first_product_jsonld(json_ld)
    product: dict[str, Any] | None = None
    if product_ld:
        image = product_ld.get("image")
        if isinstance(image, list):
            image = image[0] if image else None
        product = {
            "name": product_ld.get("name"),
            "description": product_ld.get("description"),
            "sku": product_ld.get("sku"),
            "brand": product_ld.get("brand"),
            "image": image,
            **_normalize_offer(product_ld.get("offers")),
        }

    open_graph = {
        "title": _meta_content(soup, prop="og:title"),
        "description": _meta_content(soup, prop="og:description"),
        "image": _meta_content(soup, prop="og:image"),
        "url": _meta_content(soup, prop="og:url"),
        "type": _meta_content(soup, prop="og:type"),
    }
    open_graph = {k: v for k, v in open_graph.items() if v is not None}

    meta = {
        "description": _meta_content(soup, name="description"),
        "robots": _meta_content(soup, name="robots"),
    }
    meta = {k: v for k, v in meta.items() if v is not None}

    return {
        "title": title,
        "canonical": canonical,
        "url": final_url,
        "meta": meta,
        "openGraph": open_graph,
        "product": product,
        "jsonLd": json_ld,
    }
