"""Job source registry — add new sources here."""

from . import remotive, jobicy, themuse, hn_hiring, adzuna, demo, claude_source

# claude_source is listed first so its results appear at the top (highest relevance)
ALL_SOURCES = [claude_source, remotive, jobicy, themuse, hn_hiring, adzuna, demo]
