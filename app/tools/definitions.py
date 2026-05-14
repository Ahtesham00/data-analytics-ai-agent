TOOL_DEFINITIONS = [
    {
        "name": "execute_sql",
        "description": (
            "Run a SELECT query against the superstore SQLite table. "
            "Returns raw rows that you will then visualise with a display tool. "
            "Only SELECT statements are permitted."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A valid SQLite SELECT statement. Only SELECT is permitted.",
                },
                "description": {
                    "type": "string",
                    "description": "One sentence describing what this query fetches.",
                },
            },
            "required": ["sql"],
        },
    },
    {
        "name": "display_kpi_card",
        "description": (
            "Render a single headline metric as a prominent KPI card. "
            "Use for one aggregated number like total revenue or overall profit margin."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title":    {"type": "string", "description": "Short metric label, e.g. 'Total Revenue'"},
                "value":    {"type": "string", "description": "Formatted display value, e.g. '$2.3M' or '12.5%'"},
                "subtitle": {"type": "string", "description": "Context line, e.g. 'All regions, 2014–2017'"},
                "trend": {
                    "type": "object",
                    "description": "Optional period-over-period change",
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down", "neutral"]},
                        "value":     {"type": "string", "description": "e.g. '+8.3%'"},
                        "label":     {"type": "string", "description": "e.g. 'vs prior year'"},
                    },
                    "required": ["direction", "value"],
                },
                "color": {
                    "type": "string",
                    "enum": ["default", "green", "red", "blue", "yellow", "purple"],
                    "description": "Accent colour. Use green for positive metrics, red for losses.",
                },
            },
            "required": ["title", "value"],
        },
    },
    {
        "name": "display_stat_block",
        "description": (
            "Render 2–4 related KPI cards side-by-side in a grid. "
            "Use when the user asks for a summary with multiple related metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "stats": {
                    "type": "array",
                    "description": "2–4 KPI objects.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title":    {"type": "string"},
                            "value":    {"type": "string"},
                            "subtitle": {"type": "string"},
                            "color":    {"type": "string", "enum": ["default","green","red","blue","yellow","purple"]},
                        },
                        "required": ["title", "value"],
                    },
                    "minItems": 2,
                    "maxItems": 4,
                },
            },
            "required": ["stats"],
        },
    },
    {
        "name": "display_line_chart",
        "description": (
            "Display a time-series trend or any data over a continuous/ordered x-axis. "
            "Best for monthly revenue, quarterly profit trends, running totals."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title":       {"type": "string"},
                "description": {"type": "string", "description": "1–2 sentence insight about this chart"},
                "data": {
                    "type": "array",
                    "description": "Array of row objects from execute_sql",
                    "items": {"type": "object"},
                },
                "x_key": {"type": "string", "description": "Key for the x-axis, e.g. 'month'"},
                "y_keys": {
                    "type": "array",
                    "description": "One or more y-axis series to plot.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key":   {"type": "string"},
                            "label": {"type": "string"},
                            "color": {"type": "string", "enum": ["blue","green","purple","orange","red","yellow"]},
                        },
                        "required": ["key", "label"],
                    },
                },
                "value_prefix": {"type": "string", "description": "e.g. '$' for currency axes"},
                "value_suffix": {"type": "string", "description": "e.g. '%' for percentage axes"},
            },
            "required": ["title", "data", "x_key", "y_keys"],
        },
    },
    {
        "name": "display_bar_chart",
        "description": (
            "Compare a metric across discrete categories. "
            "Best for sales by region, profit by product category, top-N rankings."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title":       {"type": "string"},
                "description": {"type": "string"},
                "data": {
                    "type": "array",
                    "items": {"type": "object"},
                },
                "x_key": {"type": "string"},
                "y_keys": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key":   {"type": "string"},
                            "label": {"type": "string"},
                            "color": {"type": "string", "enum": ["blue","green","purple","orange","red","yellow"]},
                        },
                        "required": ["key", "label"],
                    },
                },
                "value_prefix": {"type": "string"},
                "value_suffix": {"type": "string"},
                "orientation": {
                    "type": "string",
                    "enum": ["vertical", "horizontal"],
                    "default": "vertical",
                    "description": "Use horizontal when x-axis labels are long.",
                },
                "show_negative_color": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, bars with negative y-values render in red.",
                },
            },
            "required": ["title", "data", "x_key", "y_keys"],
        },
    },
    {
        "name": "display_table",
        "description": (
            "Show a result set as a sortable formatted table. "
            "Best for top-N ranked lists, multi-column breakdowns, or any result where individual rows carry meaning."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title":       {"type": "string"},
                "description": {"type": "string"},
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key":   {"type": "string"},
                            "label": {"type": "string"},
                            "type":  {
                                "type": "string",
                                "enum": ["string", "number", "currency", "percent", "date"],
                            },
                            "align": {"type": "string", "enum": ["left", "right", "center"]},
                        },
                        "required": ["key", "label"],
                    },
                },
                "data": {"type": "array", "items": {"type": "object"}},
                "default_sort":  {"type": "string"},
                "default_order": {"type": "string", "enum": ["asc", "desc"]},
            },
            "required": ["title", "columns", "data"],
        },
    },
    {
        "name": "display_suggestion_chips",
        "description": (
            "Render 2–4 clickable follow-up question chips below the response. "
            "MUST be called at the end of EVERY assistant response without exception."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label":  {"type": "string", "description": "Short chip label, ≤40 chars"},
                            "prompt": {"type": "string", "description": "Full question submitted when clicked"},
                        },
                        "required": ["label", "prompt"],
                    },
                    "minItems": 2,
                    "maxItems": 4,
                },
            },
            "required": ["suggestions"],
        },
    },
    {
        "name": "display_dropdown_filter",
        "description": (
            "Render an interactive dropdown control. "
            "When the user changes the selection, a new message is sent automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "label": {"type": "string", "description": "e.g. 'Filter by Region'"},
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label":  {"type": "string"},
                            "prompt": {"type": "string"},
                        },
                        "required": ["label", "prompt"],
                    },
                },
                "default_option_index": {"type": "integer", "default": 0},
            },
            "required": ["label", "options"],
        },
    },
]

DISPLAY_TOOL_NAMES = {
    "display_kpi_card",
    "display_stat_block",
    "display_line_chart",
    "display_bar_chart",
    "display_table",
    "display_suggestion_chips",
    "display_dropdown_filter",
}
