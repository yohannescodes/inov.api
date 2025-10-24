from __future__ import annotations

import html
from typing import Any

import httpx

from app.core.config import settings


def _render_marks(text: str, marks: list[str] | None, mark_defs: dict[str, dict[str, Any]]) -> str:
    rendered = html.escape(text)
    if not marks:
        return rendered

    for mark in marks:
        if mark == 'strong':
            rendered = f'<strong>{rendered}</strong>'
        elif mark == 'em':
            rendered = f'<em>{rendered}</em>'
        elif mark == 'code':
            rendered = f'<code>{rendered}</code>'
        elif mark in mark_defs:
            definition = mark_defs[mark]
            if definition.get('_type') == 'link':
                href = html.escape(definition.get('href', '#'), quote=True)
                rendered = f'<a href="{href}" target="_blank" rel="noopener noreferrer">{rendered}</a>'
    return rendered


def _render_block_children(block: dict[str, Any]) -> str:
    mark_defs = {definition.get('_key'): definition for definition in block.get('markDefs', [])}
    children = block.get('children') or []
    rendered_children = [_render_marks(child.get('text', ''), child.get('marks'), mark_defs) for child in children]
    return ''.join(rendered_children) or '&nbsp;'


def _render_block(block: dict[str, Any]) -> tuple[str | None, str]:
    """Return a tuple of (list_tag, html) where list_tag indicates ul/ol when needed."""
    style = block.get('style', 'normal')
    list_item = block.get('listItem')
    html_inner = _render_block_children(block)

    if list_item:
        tag = 'ul' if list_item == 'bullet' else 'ol'
        return tag, f'<li>{html_inner}</li>'

    tag_map = {
        'normal': 'p',
        'h2': 'h2',
        'h3': 'h3',
        'h4': 'h4',
        'blockquote': 'blockquote',
    }
    tag = tag_map.get(style, 'p')
    return None, f'<{tag}>{html_inner}</{tag}>'


def _render_pull_quote(block: dict[str, Any]) -> str:
    text = html.escape(block.get('text', ''))
    attribution = block.get('attribution')
    cite = f'<cite>{html.escape(attribution)}</cite>' if attribution else ''
    return f'<blockquote class="pull-quote"><p>{text}</p>{cite}</blockquote>'


def _render_callout(block: dict[str, Any]) -> str:
    title = block.get('title')
    tone = block.get('tone') or 'default'
    body_segments = [html.escape(segment) for segment in (block.get('body') or '').splitlines() if segment]
    body_html = '<br>'.join(body_segments) if body_segments else ''
    title_html = f'<p class="callout__title">{html.escape(title)}</p>' if title else ''
    return f'<aside class="callout callout--{tone}">{title_html}<p>{body_html}</p></aside>'


def _render_ritual_step(block: dict[str, Any]) -> str:
    title = html.escape(block.get('title', 'Step'))
    description_segments = [html.escape(segment) for segment in (block.get('description') or '').splitlines() if segment]
    description_html = '<br>'.join(description_segments)
    return f'<section class="ritual-step"><h4>{title}</h4><p>{description_html}</p></section>'


def portable_text_to_html(blocks: list[dict[str, Any]] | None) -> str:
    if not blocks:
        return ''

    html_parts: list[str] = []
    current_list: str | None = None

    for block in blocks:
        block_type = block.get('_type')
        if block_type == 'block':
            list_tag, block_html = _render_block(block)
            if list_tag:
                if current_list != list_tag:
                    if current_list:
                        html_parts.append(f'</{current_list}>')
                    html_parts.append(f'<{list_tag}>')
                    current_list = list_tag
                html_parts.append(block_html)
            else:
                if current_list:
                    html_parts.append(f'</{current_list}>')
                    current_list = None
                html_parts.append(block_html)
        elif block_type == 'pullQuote':
            if current_list:
                html_parts.append(f'</{current_list}>')
                current_list = None
            html_parts.append(_render_pull_quote(block))
        elif block_type == 'callout':
            if current_list:
                html_parts.append(f'</{current_list}>')
                current_list = None
            html_parts.append(_render_callout(block))
        elif block_type == 'ritualStep':
            if current_list:
                html_parts.append(f'</{current_list}>')
                current_list = None
            html_parts.append(_render_ritual_step(block))

    if current_list:
        html_parts.append(f'</{current_list}>')

    return ''.join(html_parts)


async def fetch_entries(category: str | None = None) -> list[dict[str, Any]]:
    filters = ['_type == "novarchEntry"', 'status == "published"']
    params: dict[str, Any] = {}
    if category:
        filters.append('category->slug.current == $category')
        params['$category'] = category

    filter_expression = ' && '.join(filters)
    query = (
        f"*[{filter_expression}] | order(publishedAt desc){{"
        " _id, title, subtitle, \"slug\": slug.current, \"category\": category->slug.current,"
        " summary, body, publishedAt, _createdAt, _updatedAt }"
    )

    query_params = {'query': query}
    query_params.update(params)

    headers: dict[str, str] = {}
    if settings.sanity_token:
        headers['Authorization'] = f'Bearer {settings.sanity_token}'

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(settings.sanity_dataset_url, params=query_params, headers=headers)
        response.raise_for_status()
        payload = response.json()

    results = payload.get('result', []) if isinstance(payload, dict) else []

    entries: list[dict[str, Any]] = []
    for item in results:
        entry = {
            'id': item.get('_id'),
            'title': item.get('title'),
            'subtitle': item.get('subtitle'),
            'slug': item.get('slug'),
            'category': item.get('category'),
            'summary': item.get('summary'),
            'content_html': portable_text_to_html(item.get('body')),
            'created_at': item.get('_createdAt'),
            'updated_at': item.get('_updatedAt'),
            'published_at': item.get('publishedAt'),
        }
        entries.append(entry)

    return entries


async def fetch_entry_by_slug(slug: str) -> dict[str, Any] | None:
    filters = [
        '_type == "novarchEntry"',
        'status == "published"',
        'slug.current == $slug',
    ]
    filter_expression = ' && '.join(filters)
    query = (
        f"*[{filter_expression}][0]{{"
        " _id, title, subtitle, \"slug\": slug.current, \"category\": category->slug.current,"
        " summary, body, publishedAt, _createdAt, _updatedAt }"
    )

    query_params = {'query': query, '$slug': slug}

    headers: dict[str, str] = {}
    if settings.sanity_token:
        headers['Authorization'] = f'Bearer {settings.sanity_token}'

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(settings.sanity_dataset_url, params=query_params, headers=headers)
        response.raise_for_status()
        payload = response.json()

    result = payload.get('result') if isinstance(payload, dict) else None
    if not result:
        return None

    return {
        'id': result.get('_id'),
        'title': result.get('title'),
        'subtitle': result.get('subtitle'),
        'slug': result.get('slug'),
        'category': result.get('category'),
        'summary': result.get('summary'),
        'content_html': portable_text_to_html(result.get('body')),
        'created_at': result.get('_createdAt'),
        'updated_at': result.get('_updatedAt'),
        'published_at': result.get('publishedAt'),
    }
